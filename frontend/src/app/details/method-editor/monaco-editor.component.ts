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
import { editor as MonacoEditor } from '@codingame/monaco-vscode-editor-api';
import { MonacoEditorLanguageClientWrapper } from 'monaco-editor-wrapper';
import { Observable } from 'rxjs';
import { MonacoEditorBehaviours } from './monaco-editor-behaviours';
import { MonacoWrapperConfig } from './monaco-wrapper-config';


@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['monaco-editor.component.scss'],
  template: `
    <div #editor class="w-full h-full"></div>
  `,
})
export class MonacoEditorComponent implements AfterViewInit {
  editorSizeChange = input.required<Observable<void>>();
  unitId = input<string>();
  editorContent = input<string>();
  editorOptions = input<MonacoEditor.IEditorOptions & MonacoEditor.IGlobalEditorOptions>({});
  @Output() editorContentChanged = new EventEmitter<string[]>();
  @Output() editorIsReady = new EventEmitter<MonacoEditor.IStandaloneCodeEditor>();
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private wrapper = new MonacoEditorLanguageClientWrapper();

  constructor(private injector: Injector, private destroyRef: DestroyRef) {}

  async ngAfterViewInit() {
    await this.initAndStartWrapper();
    runInInjectionContext(this.injector, this.setupEditorBehaviours.bind(this));
    await this.startLanguageClient();
    this.editorIsReady.emit(this.wrapper.getEditor());
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
    new MonacoEditorBehaviours(this.destroyRef, editor, this.editorSizeChange(), this.editorContent,
      this.onEditorContentChanged.bind(this));
  }

  private onEditorContentChanged(lines: string[]) {
    this.editorContentChanged.emit(lines);
  }

  private async initAndStartWrapper() {
    const wrapperConfig = MonacoWrapperConfig.buildWrapperUserConfig(this.editorElement.nativeElement, this.editorContent(),
      this.unitId());
    await this.wrapper.initAndStart(wrapperConfig, false);
    this.destroyRef.onDestroy(() => this.wrapper.dispose());
  }
}
