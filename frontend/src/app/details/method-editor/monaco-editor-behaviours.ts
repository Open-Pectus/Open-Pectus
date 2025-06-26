import { DestroyRef, effect, Signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MenuItemAction } from '@codingame/monaco-vscode-api/vscode/vs/platform/actions/common/actions';
import { editor as MonacoEditor } from '@codingame/monaco-vscode-editor-api';
import { Observable } from 'rxjs';


interface EditorContributionWithMenuActions extends MonacoEditor.IEditorContribution {
  _getMenuActions: () => MenuItemAction[];
}

// Behaviours common among all instances of Monaco Editor
export class MonacoEditorBehaviours {
  constructor(private destroyRef: DestroyRef,
              private editor: MonacoEditor.IStandaloneCodeEditor,
              private editorSizeChange: Observable<void>,
              private editorContentSignal: Signal<string | undefined>,
              private onEditorContentChanged?: (lines: string[]) => void) {
    this.setupOnEditorChanged();
    this.setupReactingToResize();
    this.setupContextMenuOverrides();
    this.setupOnEditorContentSignalChanged();
  }

  private setupOnEditorChanged() {
    if(this.onEditorContentChanged === undefined) return;
    const onEditorContentChanged = this.onEditorContentChanged;
    this.editor.onDidChangeModelContent(() => {
      const model = this.editor.getModel();
      if(model === null) return;
      onEditorContentChanged(model.getLinesContent());
    });
  }

  private setupReactingToResize() {
    const layoutEditor = () => this.editor.layout(undefined, true);
    this.editorSizeChange.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(layoutEditor);
    window.addEventListener('resize', layoutEditor);
    this.destroyRef.onDestroy(() => window.removeEventListener('resize', layoutEditor));
  }

  // adapted from https://github.com/CodinGame/monaco-vscode-api/issues/596#issuecomment-2711135557
  private setupContextMenuOverrides() {
    const contextmenu = this.editor.getContribution('editor.contrib.contextmenu') as EditorContributionWithMenuActions | null;
    if(contextmenu === null) return;

    const realMethod = contextmenu._getMenuActions;
    contextmenu._getMenuActions = (...args) => {
      const items = realMethod.apply(contextmenu, args);
      return items.filter((item) => item.id !== 'workbench.action.showCommands');
    };
  }

  private setupOnEditorContentSignalChanged() {
    effect(() => {
      const signalValue = this.editorContentSignal();
      if(signalValue === undefined) return;
      const modelValue = this.editor.getModel()?.getLinesContent().join('\n');
      if(modelValue !== signalValue) this.editor.setValue(signalValue);
    });
  }
}
