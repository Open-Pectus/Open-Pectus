from __future__ import annotations
from enum import Enum
import logging
from typing import List

from lang.model.pprogram import (
    PNode,
    PProgram,
    PBlank,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PCommand,
    PMark,
)

from lang.exec.tags import (
    TagCollection,
    DEFAULT_TAG_BLOCK_TIME,
    DEFAULT_TAG_RUN_TIME,
)
from lang.exec.uod import UnitOperationDefinitionBase
from lang.exec.pinterpreter import PNodeVisitor


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AnalyzerItemType(Enum):
    HINT = 'HINT',
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR'


class AnalyzerItem():
    def __init__(self,
                 id: str,
                 message: str,
                 node: PNode | None,
                 type: AnalyzerItemType,
                 description: str = "") -> None:

        self.id: str = id
        self.message: str = message
        self.description: str = description
        self.type: AnalyzerItemType = type
        self.node: PNode | None = node


class AnalyzerVisitorBase(PNodeVisitor):
    """ Override by specific feature analyzers. """

    def __init__(self) -> None:
        super().__init__()
        self.items: List[AnalyzerItem] = []

    def add_item(self, item: AnalyzerItem):
        self.items.append(item)

    def visit_children(self, children: List[PNode] | None):
        if children is not None:
            for child in children:
                self.visit(child)

    def visit_PProgram(self, node: PProgram):
        self.visit_children(node.children)

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        pass

    def visit_PBlock(self, node: PBlock):
        self.visit_children(node.children)

    def visit_PEndBlock(self, node: PEndBlock):
        pass

    def visit_PWatch(self, node: PWatch):
        self.visit_children(node.children)


class UnreachableCodeVisitor(AnalyzerVisitorBase):

    def create_item(self, node: PNode):
        return AnalyzerItem(
            "UnreachableCode",
            "Unreachable code",
            node,
            AnalyzerItemType.WARNING,
            "There is no path to this code."
        )

    def visit_PBlock(self, node: PBlock):
        has_end = False
        if node.children is not None:
            for child in node.children:
                if isinstance(child, (PEndBlock, PEndBlocks)):
                    has_end = True
                    continue
                if has_end:
                    self.add_item(self.create_item(child))


class InfiniteBlockVisitor(AnalyzerVisitorBase):

    def create_item(self, node: PNode):
        return AnalyzerItem(
            "InfiniteBlock",
            "Infinite block",
            node,
            AnalyzerItemType.WARNING,
            "This block will run indefinitely, as there are no End block or End blocks to terminate it."
        )

    def __init__(self) -> None:
        super().__init__()
        self.has_global_end = False
        self.requires_global_end = []

    def check_global_end_block(self, node: PEndBlock | PEndBlocks):
        p = node.parent
        while p is not None:
            if isinstance(p, (PWatch, PAlarm)):
                if isinstance(p.parent, PProgram):
                    self.has_global_end = True
                    break
            p = p.parent

    def check_local_end_block(self, node: PBlock):
        for child in node.get_child_nodes(recursive=True):
            if isinstance(child, (PEndBlock, PEndBlocks)):
                return True
        return False

    def visit_PProgram(self, node: PProgram):
        super().visit_PProgram(node)

        if len(self.requires_global_end) > 0 and not self.has_global_end:
            for node in self.requires_global_end:
                self.add_item(self.create_item(node))

    def visit_PBlock(self, node: PBlock):
        super().visit_PBlock(node)

        has_end = self.check_local_end_block(node)
        # has_end = False
        # if node.children is not None:
        #     for child in node.children:
        #         if isinstance(child, (PEndBlock, PEndBlocks)):
        #             has_end = True
        #             break
        if not has_end:
            self.requires_global_end.append(node)

    def visit_PEndBlock(self, node: PEndBlock):
        self.check_global_end_block(node)

    def visit_PEndBlocks(self, node: PEndBlocks):
        self.check_global_end_block(node)


class TagsAnalyzerVisitor(AnalyzerVisitorBase):
    def __init__(self, tags: TagCollection) -> None:
        super().__init__()
        self.tags = tags

    def create_undefined(self, node: PNode, tag_name: str):
        return AnalyzerItem(
            "UndefinedTag",
            "Undefined tag",
            node,
            AnalyzerItemType.WARNING,
            f"The tag '{tag_name}' is not defined"
        )

    def visit_PWatch(self, node: PWatch):
        # TODO now is the time to add conditions to grammar/AST
        raise NotImplementedError()
        # node.condition.tag_name
        # self.visit_children(node.children)


class SemanticAnalyzer(PNodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[AnalyzerItem] = []
        self.analyzers = [
            UnreachableCodeVisitor()
        ]

    def analyze(self, program: PProgram):
        self.visit(program)
        for analyzer in self.analyzers:
            self.items.extend(analyzer.items)

    @property
    def errors(self) -> List[AnalyzerItem]:
        return list([i for i in self.items if i.type == AnalyzerItemType.ERROR])

    @property
    def warnings(self) -> List[AnalyzerItem]:
        return list([i for i in self.items if i.type == AnalyzerItemType.ERROR])

    def visit_children(self, children: List[PNode] | None):
        if children is not None:
            for child in children:
                self.visit(child)

    def visit_PProgram(self, node: PProgram):
        self.visit_children(node.children)

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        pass

    def visit_PBlock(self, node: PBlock):
        self.visit_children(node.children)

    def visit_PEndBlock(self, node: PEndBlock):
        pass
