import { createAction, props } from '@ngrx/store';
import { BatchJob, CommandExample, ControlState, ExecutableCommand, ProcessDiagram, ProcessValue } from '../../api';

const source = '[Details] ';

export class DetailsActions {
  static unitDetailsInitialized = createAction(source + 'Unit Details Initialized', props<{ unitId: string }>());
  static unitDetailsDestroyed = createAction(source + 'Unit Details Destroyed');
  static processValuesFetched = createAction(source + 'Process Values Fetched', props<{ processValues: ProcessValue[] }>());
  static processValuesFailedToLoad = createAction(source + 'Process Values Failed to load');
  static processUnitCommandButtonClicked = createAction(source + 'Process Unit Command Button Clicked',
    props<{ command: string }>());
  static processDiagramInitialized = createAction(source + 'Process Diagram Initialized');
  static processDiagramFetched = createAction(source + 'Process Diagram Fetched', props<{ processDiagram: ProcessDiagram }>());
  static commandsComponentInitialized = createAction(source + 'Commands Component Initialized');
  static commandExamplesFetched = createAction(source + 'Command Examples Fetched', props<{ commandExamples: CommandExample[] }>());
  static commandsComponentExecuteClicked = createAction(source + 'Commands Component Execute Clicked', props<{ command: ExecutableCommand }>());
  static controlStateFetched = createAction(source + 'Control State Fetched', props<{ controlState: ControlState }>());
  static batchJobDetailsInitialized = createAction(source + 'Batch Job Details Initialized');
  static batchJobDetailsDestroyed = createAction(source + 'Batch Job Details Destroyed');
  static batchJobFetched = createAction(source + 'Batch Job Fetched', props<{ batchJob: BatchJob }>());
  static batchJobDownloadCsvButtonClicked = createAction(source + 'Batch Job Download Csv Button Clicked', props<{ batchJobId: string }>());
  static controlStateUpdatedOnBackend = createAction(source + 'Control State Updated On Backend', props<{ unitId: string }>());
}
