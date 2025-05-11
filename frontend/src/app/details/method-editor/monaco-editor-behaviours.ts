import { Signal } from '@angular/core';
import { editor as MonacoEditor, KeyCode, Range, KeyMod } from '@codingame/monaco-vscode-editor-api';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { combineLatest, filter, Observable, takeUntil } from 'rxjs';
import { MethodLine } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

const startedLineClassName = 'started-line';
const executedLineClassName = 'executed-line';
const injectedLineClassName = 'injected-line';
const lineIdClassNamePrefix = 'line-id-';

export class MonacoEditorBehaviours {
  private executedLineIds = this.store.select(MethodEditorSelectors.executedLineIds);
  private injectedLineIds = this.store.select(MethodEditorSelectors.injectedLineIds);
  private startedLineIds = this.store.select(MethodEditorSelectors.startedLineIds);
  private lineIds = this.store.select(MethodEditorSelectors.lineIds);
  private methodLines = this.store.select(MethodEditorSelectors.methodLines);
  private storeModelChangedFromHere = false;
  private editorModelChangedFromStore = false;

  constructor(private store: Store,
              private componentDestroyed: Observable<void>,
              private editor: MonacoEditor.IStandaloneCodeEditor,
              private readOnlyEditor: Signal<boolean>,
              private editorSizeChange: Observable<void>) {
    this.setupOnEditorChanged();
    this.setupOnStoreModelChanged();
    this.setupInjectedLines();
    this.setupStartedAndExecutedLines();
    this.setupReactingToResize();
    this.setupCtrlSAction();
  }

  private setupCtrlSAction() {
    this.editor.addCommand(KeyMod.CtrlCmd | KeyCode.KeyS, () => {
      this.store.dispatch(MethodEditorActions.saveKeyboardShortcutPressed());
    })
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

  private setupStartedAndExecutedLines() {
    const startedAndExecutedLinesDecorationCollection = this.setupDecoratingStartedAndExecutedLines();
    if(this.readOnlyEditor()) {
      this.editor.updateOptions({readOnly: true, readOnlyMessage: {value: 'You cannot edit an already executed program.'}});
    } else {
      this.setupLockingStartedAndExecutedLines(startedAndExecutedLinesDecorationCollection);
    }
  }

  private setupLockingStartedAndExecutedLines(startedAndExecutedLineDecorations: MonacoEditor.IEditorDecorationsCollection) {
    const lockEditorIfSelectionIntersectsExecutedLines = () => {
      const selectionInLockedRange = this.editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            return selection.intersectRanges(new Range(lockedLineNumber, 0, lockedLineNumber + 1, 0));
          });
      });
      this.editor.updateOptions({readOnly: selectionInLockedRange, readOnlyMessage: {value: 'Cannot edit lines already started or executed.'}});
    };
    this.editor.onDidChangeCursorSelection(lockEditorIfSelectionIntersectsExecutedLines);
    this.executedLineIds.pipe(takeUntil(this.componentDestroyed)).subscribe(lockEditorIfSelectionIntersectsExecutedLines);

    // Block specifically delete/backspace when at the ending/starting edge of the line before/after the locked line.
    this.editor.onKeyDown(event => {
      const isBackspace = event.keyCode === KeyCode.Backspace;
      const isDelete = event.keyCode === KeyCode.Delete;
      if(!isBackspace && !isDelete) return;
      const selectionInLockedRange = this.editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
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
        createDecoration(lineIds, executedLineClassName, 'This line has been executed and is no longer editable.'),
      );
      const startedLinesDecorations = startedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, startedLineClassName, 'This line has been started and is no longer editable.'),
      );
      startedAndExecutedLinesDecorationsCollection.set([...executedLinesDecorations, ...startedLinesDecorations]);
    });
    return startedAndExecutedLinesDecorationsCollection;
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
            linesDecorationsClassName: 'codicon-export codicon',
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

  private setupReactingToResize() {
    this.editorSizeChange.pipe(takeUntil(this.componentDestroyed)).subscribe(() => this.editor.layout());
    window.onresize = () => this.editor.layout();
  }
}
