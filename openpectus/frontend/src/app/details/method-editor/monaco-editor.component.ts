import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
// import '@codingame/monaco-vscode-json-default-extension';
import '@codingame/monaco-vscode-theme-defaults-default-extension';
import { IExtensionManifest, registerExtension } from '@codingame/monaco-vscode-api/extensions';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { editor as MonacoEditor, KeyCode, Range } from 'monaco-editor';
import { MonacoEditorLanguageClientWrapper, WrapperConfig } from 'monaco-editor-wrapper';
import { Logger } from 'monaco-languageclient/tools';
import { useWorkerFactory } from 'monaco-languageclient/workerFactory';
import { combineLatest, filter, firstValueFrom, Observable, Subject, takeUntil } from 'rxjs';
import { LogLevel } from 'vscode';
import { MethodLine } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

const startedLineClassName = 'started-line';
const executedLineClassName = 'executed-line';
const injectedLineClassName = 'injected-line';
const lineIdClassNamePrefix = 'line-id-';

// Extension registration adapted from @codingame/monaco-vscode-json-default-extension. Needed for LSP communication.
const manifest = {
  name: 'pcode',
  version: '0.0.0',
  publisher: 'openpectus',
  engines: {vscode: '0.10.x'},
  categories: ['Programming Languages'],
  contributes: {
    languages: [{
      id: 'pcode',
      aliases: ['PCODE', 'pcode'],
      extensions: ['.pcode'],
      mimetypes: ['application/pcode'],
      // configuration: './language-configuration.json', // can be used to configure things like indentation and autoclosing brackets, see file in @codingame/monaco-vscode-json-default-extension
    }],
  },
  main: undefined,
} satisfies IExtensionManifest;

registerExtension(manifest, undefined, {'system': true});


@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['monaco-editor.component.scss'],
  template: `
    <div #editor class="w-full h-full"></div>
  `,
})
export class MonacoEditorComponent implements AfterViewInit, OnDestroy {
  @Input() editorSizeChange?: Observable<void>;
  @Input() readOnlyEditor = false;
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private editor?: MonacoEditor.IStandaloneCodeEditor;
  private wrapper = new MonacoEditorLanguageClientWrapper();
  private methodContent = this.store.select(MethodEditorSelectors.methodContent);
  private executedLineIds = this.store.select(MethodEditorSelectors.executedLineIds);
  private injectedLineIds = this.store.select(MethodEditorSelectors.injectedLineIds);
  private startedLineIds = this.store.select(MethodEditorSelectors.startedLineIds);
  private lineIds = this.store.select(MethodEditorSelectors.lineIds);
  private methodLines = this.store.select(MethodEditorSelectors.methodLines);
  private storeModelChangedFromHere = false;
  private editorModelChangedFromStore = false;

  constructor(private store: Store) {}

  configureMonacoWorkers(logger?: Logger) {
    useWorkerFactory({
      workerLoaders: {
        'TextEditorWorker': () => new Worker(new URL('@codingame/monaco-vscode-editor-api/esm/vs/editor/editor.worker.js', import.meta.url),
          {type: 'module'}),
        'TextMateWorker': () => new Worker(new URL('@codingame/monaco-vscode-textmate-service-override/worker', import.meta.url),
          {type: 'module'}),
        OutputLinkDetectionWorker: undefined,
        LanguageDetectionWorker: undefined,
        NotebookEditorWorker: undefined,
        LocalFileSearchWorker: undefined,
      },
      logger,
    });
  };

  async ngAfterViewInit() {
    const methodContent = await firstValueFrom(this.methodContent);
    await this.wrapper.initAndStart(this.buildWrapperUserConfig(this.editorElement.nativeElement, methodContent));
    // @ts-expect-error they seem to point to the same type, but from different packages
    this.editor = this.wrapper.getEditor();
    this.setupEditor(this.editor);

    this.editorSizeChange?.pipe(takeUntil(this.componentDestroyed)).subscribe(() => this.editor?.layout());
    window.onresize = () => this.editor?.layout();
    this.store.dispatch(MethodEditorActions.monacoEditorComponentInitialized());
  }

  buildWrapperUserConfig(htmlContainer: HTMLElement, text: string): WrapperConfig {
    return {
      $type: 'extended',
      htmlContainer,
      logLevel: LogLevel.Debug,
      vscodeApiConfig: {
        // vscodeApiInitPerformExternally: true,
        // enableExtHostWorker: true,
        userConfiguration: {
          json: JSON.stringify({ // TODO: find documentation for this, and adapt the previous configuration to new
            fontSize: 18,
            glyphMargin: false,
            fixedOverflowWidgets: true,
            lineNumbersMinChars: UtilMethods.isMobile ? 1 : 3,
            minimap: {
              enabled: UtilMethods.isDesktop,
            },
            autoIndent: 'none',
            'editor.lightbulb.enabled': 'off',
            'editor.experimental.asyncTokenization': true,
          }),
        },
      },
      editorAppConfig: {
        codeResources: {
          modified: {
            text,
            fileExt: 'pcode',
          },
        },
        monacoWorkerFactory: this.configureMonacoWorkers,
      },
      languageClientConfigs: {
        pcode: {
          clientOptions: {
            documentSelector: ['pcode'],
          },
          connection: {
            options: {
              $type: 'WebSocketUrl',
              url: 'ws://localhost:30000/sampleServer',
              startOptions: {
                onCall: () => {
                  console.log('Connected to socket.');
                },
                reportStatus: true,
              },
              stopOptions: {
                onCall: () => {
                  console.log('Disconnected from socket.');
                },
                reportStatus: true,
              },
            },
          },
        },
      },
    } satisfies WrapperConfig;
  };

  ngOnDestroy() {
    this.componentDestroyed.next();
    void this.wrapper.dispose();
    this.store.dispatch(MethodEditorActions.monacoEditorComponentDestroyed());
  }

  private setupEditor(editor?: MonacoEditor.IStandaloneCodeEditor) {
    if(editor === undefined) return;
    // const editor = await this.constructEditor();
    this.setupOnEditorChanged(editor);
    this.setupOnStoreModelChanged(editor);
    this.setupInjectedLines(editor);
    this.setupStartedAndExecutedLines(editor);

    // return editor;
  }

  private setupOnEditorChanged(editor: MonacoEditor.IStandaloneCodeEditor) {
    editor.onDidChangeModelContent(() => {
      if(this.editorModelChangedFromStore) return;
      setTimeout(() => { // setTimeout to allow for line id decorations to be placed before this is executed
        const model = editor.getModel();
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
  private setupOnStoreModelChanged(editor: MonacoEditor.IStandaloneCodeEditor) {
    const lineIdsDecorationCollection = editor.createDecorationsCollection();
    this.methodLines.pipe(
      filter(() => !this.storeModelChangedFromHere),
      takeUntil(this.componentDestroyed),
    ).subscribe(methodLines => {
      // Apply edits
      const methodContent = methodLines.map(line => line.content).join('\n');
      const preEditSelection = editor.getSelection();

      this.editorModelChangedFromStore = true;
      editor.getModel()?.applyEdits([{range: new Range(0, 0, Number.MAX_VALUE, Number.MAX_VALUE), text: methodContent}]);
      this.editorModelChangedFromStore = false;

      if(preEditSelection !== null) editor.setSelection(preEditSelection);

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

  private setupStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const startedAndExecutedLinesDecorationCollection = this.setupDecoratingStartedAndExecutedLines(editor);
    if(this.readOnlyEditor) {
      editor.updateOptions({readOnly: true, readOnlyMessage: {value: 'You cannot edit an already executed program.'}});
    } else {
      this.setupLockingStartedAndExecutedLines(editor, startedAndExecutedLinesDecorationCollection);
    }
  }

  private setupLockingStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor,
                                              startedAndExecutedLineDecorations: MonacoEditor.IEditorDecorationsCollection) {
    const lockEditorIfSelectionIntersectsExecutedLines = () => {
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            return selection.intersectRanges(new Range(lockedLineNumber, 0, lockedLineNumber + 1, 0));
          });
      });
      editor.updateOptions({readOnly: selectionInLockedRange, readOnlyMessage: {value: 'Cannot edit lines already started or executed.'}});
    };
    editor.onDidChangeCursorSelection(lockEditorIfSelectionIntersectsExecutedLines);
    this.executedLineIds.pipe(takeUntil(this.componentDestroyed)).subscribe(lockEditorIfSelectionIntersectsExecutedLines);

    // Block specifically delete/backspace when at the ending/starting edge of the line before/after the locked line.
    editor.onKeyDown(event => {
      const isBackspace = event.keyCode === KeyCode.Backspace;
      const isDelete = event.keyCode === KeyCode.Delete;
      if(!isBackspace && !isDelete) return;
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            const previousLineLength = editor?.getModel()?.getLineLength(Math.max(1, lockedLineNumber - 1)) ?? 0;
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

  private setupDecoratingStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const startedAndExecutedLinesDecorationsCollection = editor.createDecorationsCollection();
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

  private decorateInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const injectedLinesDecorationCollection = editor.createDecorationsCollection();
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

  private setupInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const decorations = this.decorateInjectedLines(editor);
    decorations.onDidChange(() => {
      const lineNumbers = decorations.getRanges().flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber));
      editor.updateOptions({lineNumbers: this.getLineNumberFunction(lineNumbers)});
    });
  }
}
