import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  inject,
  Injector,
  input,
  output,
  runInInjectionContext,
  viewChild
} from '@angular/core';
// import '@codingame/monaco-vscode-json-default-extension';
// import '@codingame/monaco-vscode-theme-defaults-default-extension';
import { editor as MonacoEditor, Range } from '@codingame/monaco-vscode-editor-api';
import { ToastrService } from 'ngx-toastr';
import { Observable } from 'rxjs';
import { MonacoEditorBehaviours } from './monaco-editor-behaviours';
import { MonacoWrapper } from './monaco-wrapper';
import { EditorApp } from 'monaco-languageclient/editorApp';


@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['monaco-editor.component.scss'],
  template: `
    <div #editor class="w-full h-full" (dragover)="onDragOver($event)" (drop)="onDrop($event)"></div>
  `,
})
export class MonacoEditorComponent implements AfterViewInit {
  editorSizeChange = input.required<Observable<void>>();
  fileUriPrefix = input.required<string>();
  unitId = input<string>();
  editorContent = input<string>();
  editorOptions = input<MonacoEditor.IEditorOptions & MonacoEditor.IGlobalEditorOptions>({});
  dropFileEnabled = input<boolean>(false);
  dropFileDisabledReason = input<string>();
  readonly editorContentChanged = output<string[]>();
  readonly editorIsReady = output<MonacoEditor.IStandaloneCodeEditor>();
  readonly editorElement = viewChild.required<ElementRef<HTMLDivElement>>('editor');
  private editorApp?: EditorApp;
  private injector = inject(Injector);
  private destroyRef = inject(DestroyRef);
  private toastr = inject(ToastrService);

  async ngAfterViewInit() {
    await this.initAndStartWrapper();
    // if a collapsible element with a monaco editor starts collapsed, the above will run, but we won't have an editor afterward
    const editor = this.editorApp?.getEditor();
    if(editor === undefined) return;
    runInInjectionContext(this.injector, this.setupEditorBehaviours.bind(this));
    this.editorIsReady.emit(editor);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  async onDrop(event: DragEvent) {
    event.preventDefault();
    if(!this.dropFileEnabled()) {
      const reason = this.dropFileDisabledReason();
      if(reason !== undefined) this.showToastrError(reason);
      return;
    }
    if(this.editorOptions().readOnly) {
      this.showToastrError('Cannot replace content of readonly editor');
      return;
    }
    if(event.dataTransfer === null) {
      this.showToastrError('No datatransfer object');
      return;
    }
    const item = event.dataTransfer.items[0];
    if(item.kind !== 'file') {
      this.showToastrError('No file found in drop');
      return;
    }
    const file = item.getAsFile();

    // only accept certain file extensions
    const fileExtension = file?.name.split('.').at(-1) ?? '';
    if(!['txt', 'pcode'].includes(fileExtension)) {
      this.showToastrError('File should have extension .txt or .pcode');
      return;
    }

    const text = await file?.text();
    if(text === undefined) {
      this.showToastrError('No content found in file');
      return;
    }

    // using pushEditOperations to get undo functionality, which doesn't work with setValue or applyEdits
    const editOperation = {range: new Range(0, 0, Number.MAX_VALUE, Number.MAX_VALUE), text};
    this.editorApp?.getEditor()?.getModel()?.pushEditOperations(null, [editOperation], () => null);
  }

  private setupEditorBehaviours() {
    const editor = this.editorApp?.getEditor();
    if(editor === undefined) throw Error('Monaco Editor Wrapper returned no editor!');
    editor.updateOptions(this.editorOptions());
    new MonacoEditorBehaviours(this.destroyRef, editor, this.editorSizeChange(), this.editorContent, this.onEditorContentChanged.bind(this));
  }

  private onEditorContentChanged(lines: string[]) {
    this.editorContentChanged.emit(lines);
  }

  private async initAndStartWrapper() {
    const languageId = 'pcode';
    await MonacoWrapper.buildVsCodeApi(languageId, this.unitId());
    await MonacoWrapper.buildLanguageClient(languageId, this.unitId());

    this.editorApp = MonacoWrapper.buildEditorApp(this.fileUriPrefix());
    const htmlContainer = this.editorElement().nativeElement;
    await this.editorApp.start(htmlContainer);

    this.destroyRef.onDestroy(() => {
      this.editorApp?.dispose();
      MonacoWrapper.isInitialized = false;
    });
  }

  private showToastrError(reason: string) {
    this.toastr.error(reason, 'Drop File Failed');
  }
}
