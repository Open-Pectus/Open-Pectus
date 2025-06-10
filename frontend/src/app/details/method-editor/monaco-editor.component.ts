import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  EventEmitter,
  Injector,
  input,
  Output,
  runInInjectionContext,
  ViewChild,
} from '@angular/core';
// import '@codingame/monaco-vscode-json-default-extension';
import '@codingame/monaco-vscode-theme-defaults-default-extension';
import { editor as MonacoEditor, Range } from '@codingame/monaco-vscode-editor-api';
import { MonacoEditorLanguageClientWrapper } from 'monaco-editor-wrapper';
import { ToastrService } from 'ngx-toastr';
import { Observable } from 'rxjs';
import { MonacoEditorBehaviours } from './monaco-editor-behaviours';
import { MonacoWrapperConfig } from './monaco-wrapper-config';


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
  unitId = input<string>();
  editorContent = input<string>();
  editorOptions = input<MonacoEditor.IEditorOptions & MonacoEditor.IGlobalEditorOptions>({});
  dropFileEnabled = input<boolean>(false);
  dropFileDisabledReason = input<string>();
  @Output() editorContentChanged = new EventEmitter<string[]>();
  @Output() editorIsReady = new EventEmitter<MonacoEditor.IStandaloneCodeEditor>();
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private wrapper = new MonacoEditorLanguageClientWrapper();

  constructor(private injector: Injector, private destroyRef: DestroyRef, private toastr: ToastrService) {}

  async ngAfterViewInit() {
    await this.initAndStartWrapper();
    runInInjectionContext(this.injector, this.setupEditorBehaviours.bind(this));
    this.editorIsReady.emit(this.wrapper.getEditor());
    void this.startLanguageClient();
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
    this.wrapper.getEditor()?.getModel()?.pushEditOperations(null, [editOperation], () => null);
  }

  private async startLanguageClient() {
    if(this.unitId() !== undefined) {
      this.wrapper.initLanguageClients();
      await this.wrapper.startLanguageClients();
    }
  }

  private setupEditorBehaviours() {
    const editor = this.wrapper.getEditor();
    if(editor === undefined) throw Error('Monaco Editor Wrapper returned no editor!');
    editor.updateOptions(this.editorOptions());
    new MonacoEditorBehaviours(this.destroyRef, editor, this.editorSizeChange(), this.editorContent, this.onEditorContentChanged.bind(this));
  }

  private onEditorContentChanged(lines: string[]) {
    this.editorContentChanged.emit(lines);
  }

  private async initAndStartWrapper() {
    const wrapperConfig = MonacoWrapperConfig.buildWrapperConfig(this.editorElement.nativeElement, this.unitId());
    await this.wrapper.initAndStart(wrapperConfig);
    this.destroyRef.onDestroy(() => {
      this.wrapper.dispose();
      MonacoWrapperConfig.isInitialized = false;
    });
  }

  private showToastrError(reason: string) {
    this.toastr.error(reason, 'Drop File Failed');
  }
}
