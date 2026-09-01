import { editor as MonacoEditor, KeyCode, KeyMod, Range } from '@codingame/monaco-vscode-editor-api';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { combineLatest, filter, Observable, takeUntil } from 'rxjs';
import { MethodLine } from 'src/app/api';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

const startedLineClassName = 'started-line';
const executedLineClassName = 'executed-line';
const injectedLineClassName = 'injected-line';
const lockedLineClassName = 'locked-line';
const contentLockedLineClassName = 'content-locked-line';
const lineIdClassNamePrefix = 'line-id-';

// Behaviours only for the method editor
export class MethodEditorBehaviours {
  private executedLineIds = this.store.select(MethodEditorSelectors.executedLineIds);
  private injectedLineIds = this.store.select(MethodEditorSelectors.injectedLineIds);
  private startedLineIds = this.store.select(MethodEditorSelectors.startedLineIds);
  // TODO look into better naming of these variables. 
  private lockedLineIds = this.store.select(MethodEditorSelectors.lockedLineIds);
  private contentLockedLineIds = this.store.select(MethodEditorSelectors.contentLockedLineIds);
  private lineIds = this.store.select(MethodEditorSelectors.lineIds);
  private methodLines = this.store.select(MethodEditorSelectors.methodLines);
  private isDirty = this.store.select(MethodEditorSelectors.isDirty);
  private storeModelChangedFromHere = false;
  private editorModelChangedFromStore = false;

  constructor(private store: Store,
              private componentDestroyed: Observable<void>,
              private editor: MonacoEditor.IStandaloneCodeEditor) {
    this.setupOnEditorChanged();
    this.setupOnStoreModelChanged();
    this.setupInjectedLines();
    this.setupLockedAndContentLockedLines();
    this.setupDecoratingStartedAndExecutedLines();
    this.setupCtrlSAction();
    this.setupDialogOnLeaveWithUnsavedChanges();
  }

  private setupOnEditorChanged() {
    this.editor.onDidChangeModelContent(() => {
      if(this.editorModelChangedFromStore) return;
      setTimeout(() => { // setTimeout to allow for line id decorations to be placed before this is executed
        const model = this.editor.getModel();
        if(model === null) return;
        const linesContents = model.getLinesContent();

        const lines = linesContents.map<MethodLine>((lineContent, index) => {
          const decorations = model.getLineDecorations(index + 1);
          const idDecoration = decorations.find(decoration => decoration.options.className?.startsWith(lineIdClassNamePrefix));
          const id = idDecoration?.options.className?.substring(lineIdClassNamePrefix.length);
          return {
            id: id ?? crypto.randomUUID(),
            content: lineContent,
          } satisfies MethodLine;
        });
        this.storeModelChangedFromHere = true;
        this.store.dispatch(MethodEditorActions.linesChanged({lines}));
        this.storeModelChangedFromHere = false;
      });
    });
  }

  // Sets up both edits to content and line id decorations, because it's important that they happen right after each other and in this order.
  private setupOnStoreModelChanged() {
    const lineIdsDecorationCollection = this.editor.createDecorationsCollection();
    this.methodLines.pipe(
      filter(() => !this.storeModelChangedFromHere),
      takeUntil(this.componentDestroyed),
    ).subscribe(methodLines => {
      // Apply edits
      const methodContent = methodLines.map(line => line.content).join('\n');
      const preEditSelection = this.editor.getSelection();

      this.editorModelChangedFromStore = true;
      this.editor.getModel()?.applyEdits([{range: new Range(0, 0, Number.MAX_VALUE, Number.MAX_VALUE), text: methodContent}]);
      this.editorModelChangedFromStore = false;

      if(preEditSelection !== null) this.editor.setSelection(preEditSelection);

      // Set line id decorations
      const lineIds = methodLines.map(line => line.id);
      const lineIdDecorations = lineIds.map<MonacoEditor.IModelDeltaDecoration>((lineId, index) => {
        const lineNumber = index + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: lineIdClassNamePrefix + lineId,
            shouldFillLineOnLineBreak: false,
            stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      lineIdsDecorationCollection.set(lineIdDecorations);
    });
  }

  private getLineNumberFunction(injectedLines: number[]) {
    return (lineNumber: number) => {
      if(injectedLines.includes(lineNumber)) return '';
      const injectedLinesBeforeThis = injectedLines.filter(injectedLineNumber => injectedLineNumber < lineNumber);
      const lineNumberWithoutInjectedLines = lineNumber - injectedLinesBeforeThis.length;
      return lineNumberWithoutInjectedLines.toString();
    };
  }

  private setupLockedAndContentLockedLines() {
    const collections = this.setupDecoratingLockedAndContentLockedLines();
    if(!this.editor.getOption(MonacoEditor.EditorOption.readOnly)) {
      this.setupLockingLockedAndContentLockedLines(collections.locked, collections.contentLocked);
    }
  }

  private setupLockingLockedAndContentLockedLines(lockedCollection: MonacoEditor.IEditorDecorationsCollection, contentLockedCollection: MonacoEditor.IEditorDecorationsCollection) {
    
    const linesFrom = (c: MonacoEditor.IEditorDecorationsCollection) =>
      c.getRanges().flatMap(r => UtilMethods.getNumberRange(r.startLineNumber, r.endLineNumber));

    const selectionIntersectsLines = (lineNumbers: number[]) =>
      this.editor.getSelections()?.some(selection =>
        lineNumbers.some(ln => selection.intersectRanges(new Range(ln, 0, ln + 1, 0))),
      ) ?? false;
    
    const lockEditorIfSelectionIntersectsLockedLines = () => {
      const inLocked = selectionIntersectsLines(linesFrom(lockedCollection));
      console.log("inLocked: " + inLocked);
      const inContentLocked = selectionIntersectsLines(linesFrom(contentLockedCollection));
      console.log("inContentLocked: " + inContentLocked);

      //TODO, what is the actual meassage here? 
      const locking = inLocked
        ? {readOnly: true, readOnlyMessage: {value: 'This line is locked.'}}
        : inContentLocked
          ? {readOnly: true, readOnlyMessage: {value: 'This line is content-locked. Press Enter to add a new line below.'}}
          : {readOnly: false, readOnlyMessage: {value: ''}};
      this.editor.updateOptions(locking);

    };
    this.editor.onDidChangeCursorSelection(lockEditorIfSelectionIntersectsLockedLines);
    this.lockedLineIds.pipe(takeUntil(this.componentDestroyed)).subscribe(lockEditorIfSelectionIntersectsLockedLines);

    // Block specifically delete/backspace when at the ending/starting edge of the line before/after the locked line.
    this.editor.onKeyDown(event => {
      const isBackspace = event.keyCode === KeyCode.Backspace;
      const isDelete = event.keyCode === KeyCode.Delete;
      if(!isBackspace && !isDelete) return;
      const selectionInLockedRange = this.editor.getSelections()?.some(selection => {
        return lockedCollection.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            const previousLineLength = this.editor?.getModel()?.getLineLength(Math.max(1, lockedLineNumber - 1)) ?? 0;
            const lockedRange = isDelete
                                ? new Range(lockedLineNumber - 1, previousLineLength + 1, lockedLineNumber, 0)
                                : new Range(lockedLineNumber, 0, lockedLineNumber + 1, 1);
            return selection.intersectRanges(lockedRange);
          });
      });
      if(selectionInLockedRange) {
        event.stopPropagation();
        event.preventDefault();
      }
    });

    this.editor.onKeyDown(event => {
      const lockedLines = linesFrom(lockedCollection);
      const contentLockedLines = linesFrom(contentLockedCollection);

      const onLocked = selectionIntersectsLines(lockedLines);
      const onContentLocked = selectionIntersectsLines(contentLockedLines);

      if (onContentLocked && !onLocked && event.keyCode === KeyCode.Enter) {
        console.log("Is content-locked");
        event.preventDefault();
        event.stopPropagation();
        const sel = this.editor.getSelection();
        if (!sel) return;
        const eol = this.editor.getModel()?.getLineMaxColumn(sel.startLineNumber) ?? 1;
        this.editor.updateOptions({ readOnly: false });
        this.editor.executeEdits('content-locked-enter', [{
          range: new Range(sel.startLineNumber, eol, sel.startLineNumber, eol),
          text: '\n',
          forceMoveMarkers: true,
        }]);
        this.editor.setPosition({lineNumber: sel.startLineNumber + 1, column: 1});
      }
    });
  }

  private setupDecoratingStartedAndExecutedLines() {
    const startedAndExecutedLinesDecorationsCollection = this.editor.createDecorationsCollection();
    const createDecoration = (lineIds: string[], lineClassName: string, hoverMessage: string) => (executedLineId: string) => {
      const lineNumber = lineIds.findIndex(lineId => lineId === executedLineId) + 1;
      if(lineNumber === undefined) throw Error(`could not find line id decoration with id ${executedLineId}`);
      return {
        range: new Range(lineNumber, 0, lineNumber, 0),
        options: {
          isWholeLine: true,
          className: lineClassName,
          hoverMessage: {value: hoverMessage},
          shouldFillLineOnLineBreak: false,
          stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
        },
      };
    };

    combineLatest([this.startedLineIds, this.executedLineIds]).pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([[startedLineIds, executedLineIds], lineIds]) => {
      const executedLinesDecorations = executedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, executedLineClassName, 'This line has been executed.'),
      );
      const startedLinesDecorations = startedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, startedLineClassName, 'This line has been started.'),
      );
      startedAndExecutedLinesDecorationsCollection.set([...executedLinesDecorations, ...startedLinesDecorations]);
    });
    return startedAndExecutedLinesDecorationsCollection;
  }

  private setupDecoratingLockedAndContentLockedLines() {
    const lockedCollection = this.editor.createDecorationsCollection();
    const contentLockedCollection = this.editor.createDecorationsCollection();
    const createDecoration = (lineIds: string[], lineClassName: string, hoverMessage: string) => (lockedLineId: string) => {
      const lineNumber = lineIds.findIndex(lineId => lineId === lockedLineId) + 1;
      if(lineNumber === undefined) throw Error(`could not find line id decoration with id ${lockedLineId}`);
      return {
        range: new Range(lineNumber, 0, lineNumber, 0),
        options: {
          isWholeLine: true,
          className: lineClassName,
          hoverMessage: {value: hoverMessage},
          shouldFillLineOnLineBreak: false,
          stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
        },
      };
    };

    combineLatest([this.contentLockedLineIds, this.lockedLineIds]).pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([[contentLockedLineIds, lockedLineIds], lineIds]) => {
      const lockedLinesDecorations = lockedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, lockedLineClassName, 'This line has been locked and is no longer editable.'),
      );
      const contentLockedLinesDecorations = contentLockedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, contentLockedLineClassName, 'This line is content-locked, only newline is allowed.'),
      );
      lockedCollection.set(lockedLinesDecorations);
      contentLockedCollection.set(contentLockedLinesDecorations);
    });
    return {locked: lockedCollection, contentLocked: contentLockedCollection};
  }

  private decorateInjectedLines() {
    const injectedLinesDecorationCollection = this.editor.createDecorationsCollection();
    this.injectedLineIds.pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([injectedLineIds, lineIds]) => {
      const injectedLinesDecorations = injectedLineIds.map<MonacoEditor.IModelDeltaDecoration>(injectedLineId => {
        const lineNumber = lineIds.findIndex(lineId => lineId === injectedLineId) + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: injectedLineClassName,
            isWholeLine: true,
            hoverMessage: {value: 'This line has been injected and is not part of the methodContent.'},
            linesDecorationsClassName: 'codicon-export codicon -ml-injected-line-icon',
            shouldFillLineOnLineBreak: false,
            stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      injectedLinesDecorationCollection.set(injectedLinesDecorations);
    });
    return injectedLinesDecorationCollection;
  }

  private setupInjectedLines() {
    const decorations = this.decorateInjectedLines();
    decorations.onDidChange(() => {
      const lineNumbers = decorations.getRanges().flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber));
      this.editor.updateOptions({lineNumbers: this.getLineNumberFunction(lineNumbers)});
    });
  }

  private setupCtrlSAction() {
    this.editor.addCommand(KeyMod.CtrlCmd | KeyCode.KeyS, () => {
      this.store.dispatch(MethodEditorActions.saveKeyboardShortcutPressed());
    });
  }

  private setupDialogOnLeaveWithUnsavedChanges() {
    this.isDirty.pipe(takeUntil(this.componentDestroyed)).subscribe(isDirty => {
      if(isDirty) {
        window.onbeforeunload = (event: Event) => event.preventDefault();
      } else {
        window.onbeforeunload = null;
      }
    });
  }
}
