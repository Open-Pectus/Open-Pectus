from __future__ import annotations
import ast
import inspect
import logging
from typing import Any, TypedDict, get_type_hints


logger = logging.getLogger(__name__)


# Impl note: using TypedDict because of its simple json serialization
class ElementState(TypedDict):
    namespace: str
    """ The namespace for the element."""
    element_id: str
    """" The id of the element. Must be unique within its namespace. """


class HasElementState():
    """ Inheriting this class enables tags, uod commands and other elements to participate in state management
    as required by live-edit and engine crash recovery.

    To do that, override apply_state and extract_state to handle the concrete state of your element.

    Example code for a custom Tag:

    class MyTag(Tag):
        def __init__(some_argument: str):
            Tag.__init__(self)  # Explicit call to Tag constructor. Do not use super().

            self.some_state: int = 7

        def extract_state(self):
            state = super().extract_state()
            state["some_state"] = self.some_state  # type: ignore
            return state

        def apply_state(self, state):
            super().apply_state(state)
            self.some_state = state["some_state"]  # type: ignore

        # tag implementation omitted ...

    """

    def __init__(self, namespace: str, element_id: str):
        if namespace is None or namespace.strip() == "":
            raise ValueError("A non-empty namespace is required")
        if element_id is None or element_id.strip() == "":
            raise ValueError("A non-empty element_id is required")

        self.namespace = namespace
        self.element_id = element_id

        # Note: element still needs to be registered. We'll leave that to the engine.

    @property
    def element_key(self) -> tuple[str, str]:
        return (self.namespace, self.element_id)

    def apply_state(self, state: ElementState):
        assert state["namespace"] == self.namespace
        assert state["element_id"] == self.element_id

        # TODO move the below to managing class and provide the above as guarantee to HasElementState instances
        if state["namespace"] != self.namespace:
            logger.error(f"Internal error: Namespace mismatch (own: '{self.namespace}', state: '{state["namespace"]}') when applying state")
        if state["element_id"] != self.element_id:
            logger.error(
                f"Internal error: Element id mismatch (own: '{self.element_id}', state: '{state["element_id"]}', namespace: {{self.namespace}})"
                + " when applying state")

    def extract_state(self) -> ElementState:
        return ElementState(
            namespace=self.namespace,
            element_id=self.element_id
        )


class ElementStateRegistry():
    def __init__(self):
        self._elements: dict[tuple[str, str], HasElementState] = {}

    def register_element(self, element: HasElementState):
        key = element.element_key
        if key in self._elements.keys():
            logger.error(f"Element with {key=} is already registered. The element is:\n{str(element)}")
        self._elements[key] = element

    def extract_all_state(self) -> dict[tuple[str, str], ElementState]:
        state: dict[tuple[str, str], ElementState] = {}
        for key, element in self._elements.items():
            try:
                state[key] = element.extract_state()
            except Exception:
                logger.error(f"Failed to extract state from element {key=}, element:\n{str(element)}", exc_info=True)
        return state

    def apply_all_state(self, state: dict[tuple[str, str], ElementState]):
        logger.info(f"Applying state to all {len(self._elements)} elements. State elements: {len(state)}")
        error_count = 0
        for key, element in self._elements.items():
            if key not in state.keys():
                logger.error(f"Element state not found. {key=} has no match in the state to apply")
                error_count += 1
            else:
                try:
                    self._elements[key].apply_state(state[key])
                except Exception:
                    logger.error(f"Failed to apply state for element {key=}, element:\n{str(element)}")
                    error_count += 1

        for key in state.keys():
            if key not in self._elements.keys():
                logger.error(f"Element not found. {key=} has no registered element for which to apply the state")
                error_count += 1

        if error_count == 0:
            logger.info("State successfully applied to all elements")
        else:
            logger.warning(f"State was partially applied, {error_count} errors occurred")

# helper method that may make it simpler to register non-tag elements
def infer_from_lambda(fn, *, instance: Any) -> tuple[str, Any | None]:
    # 1) source + AST
    src = inspect.getsource(fn)
    mod = ast.parse(src.strip())

    # 2) find the first Lambda node
    lambda_node = None
    for node in ast.walk(mod):
        if isinstance(node, ast.Lambda):
            lambda_node = node
            break
    if lambda_node is None:
        raise ValueError("No lambda found in source")

    # 3) expect body: instance.<name>
    body = lambda_node.body
    if not (isinstance(body, ast.Attribute) and isinstance(body.value, ast.Name)):
        raise ValueError("Expected lambda body like: instance.attribute")
    attr_name = body.attr

    cls = instance.__class__

    # 4) detect property vs annotated field
    # property:
    prop_obj = getattr(cls, attr_name, None)
    if isinstance(prop_obj, property):
        ret = inspect.signature(prop_obj.fget).return_annotation  # type: ignore
        if ret is inspect.Signature.empty:
            ret = None
        return attr_name, ret

    # annotated field:
    hints = get_type_hints(cls)
    type_hint = hints.get(attr_name)
    return attr_name, type_hint
