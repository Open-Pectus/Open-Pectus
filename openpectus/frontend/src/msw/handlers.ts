// noinspection DuplicatedCode

import { format, getSeconds, sub } from 'date-fns';
import { delay, http, HttpResponse, PathParams } from 'msw';
import {
  AggregatedErrorLog,
  AuthConfig,
  CommandExample,
  ControlState,
  ExecutableCommand,
  MethodAndState,
  PlotConfiguration,
  PlotLog,
  ProcessUnit,
  ProcessValue,
  RecentRun,
  RecentRunCsv,
  RunLog,
  RunLogLine,
  SystemStateEnum,
} from '../app/api';

const startedLines = [2];
const executedLines = [1, 4];
const controlState: ControlState = {
  is_running: false,
  is_holding: false,
  is_paused: false,
};
let systemState: SystemStateEnum = 'Running';

const processUnits: ProcessUnit[] = [
  {
    name: 'Some unit',
    id: 'MSW_some_unit',
    location: 'Some place',
    runtime_msec: 59999,
    state: {
      state: 'in_progress',
      progress_pct: 30,
    },
    current_user_role: 'admin',
  },
  {
    name: 'Some other unit with a long title',
    id: 'MSW_some_other_unit',
    location: 'Some place else',
    runtime_msec: 456498,
    state: {
      state: 'ready',
    },
    current_user_role: 'admin',
  },
  {
    name: 'Some third unit',
    id: 'MSW_some_third_unit',
    location: 'Some third place',
    runtime_msec: 12365,
    state: {
      state: 'not_online',
      last_seen_date: new Date().toJSON(),
    },
    current_user_role: 'admin',
  },
  {
    name: 'A fourth for linebreak',
    id: 'MSW_a_fourth',
    location: 'Narnia',
    runtime_msec: 85264,
    state: {
      state: 'error',
    },
    current_user_role: 'viewer',
  },
];

const getProcessValues: () => ProcessValue[] = () => [
  {
    value_type: 'int',
    name: 'Timestamp',
    value: new Date().valueOf(),
    direction: 'output',
  },
  {
    value_type: 'int',
    name: 'Timestamp2',
    value: new Date().valueOf() + 1000000000000,
    direction: 'output',
  },
  {
    value_type: 'float',
    name: 'PU01 Speed',
    value: 120,
    value_unit: '%',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'PU02 Speed',
    value: 121,
    value_unit: '%',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'PU03 Speed',
    value: 122,
    value_unit: '%',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'PU04 Speed',
    value: 123,
    value_unit: '%',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'PU05 Speed',
    value: 124,
    value_unit: '%',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'PU06 Speed',
    value: 125,
    value_unit: '%',
    direction: 'output',
  },
  {
    value_type: 'string',
    name: 'Some other Process Value',
    value: 'So very valuable',
    direction: 'output',
    commands: [
      {command: 'some_command', name: 'Some Command'},
      {command: 'some_other_command', name: 'Some Other Command'},
    ],
  }, {
    value_type: 'int',
    name: 'A value with unit',
    value: 1000,
    value_unit: 'm',
    direction: 'output',
    commands: [
      {
        command: 'fdsa', name: 'fdsa', value: {
          value: 1000,
          value_type: 'int',
          value_unit: 'm',
          valid_value_units: ['m', 'cm', 'mm', 'km'],
        },
      },
    ],
  }, {
    value_type: 'string',
    name: 'Many Data',
    value: 'HANDLE IT',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'FT01 Flow',
    value: 123 + Math.random() * 2,
    value_unit: 'L/h',
    direction: 'output',
    commands: [
      {
        command: 'fdsafsa',
        name: 'Set',
        value: {
          value: 123 + Math.random() * 2,
          value_unit: 'L/h',
          valid_value_units: ['L/h', 'm3/h', 'L/m', 'm3/m'],
          value_type: 'float',
        },
      },
    ],
  }, {
    value_type: 'string',
    name: 'Writable text',
    value: 'VaLuE',
    direction: 'output',
    commands: [
      {
        name: 'choice',
        command: 'choice',
        value: {
          value_type: 'choice',
          value: 'first',
          options: ['first', 'second', 'third'],
        },
      },
      {
        name: 'jiojio',
        command: 'jiojio',
        value: {
          value: 'Writable text',
          value_type: 'string',
        },
      }, {
        name: 'something',
        command: 'something',
      }, {
        name: 'something disabled',
        command: 'something disabled',
        disabled: true,
      }, {
        name: 'number',
        command: 'set number',
        value: {
          value: 123,
          value_unit: 'no',
          valid_value_units: ['no'],
          value_type: 'int',
        },
      }],
  }, {
    value_type: 'float',
    name: 'TT01',
    value: 23.4 + Math.random() * 2,
    value_unit: 'degC',
    direction: 'output',
    commands: [{
      name: 'Set target temperature',
      command: 'set_target_temperature',
      value: {
        value: 23.4 + Math.random() * 2,
        value_unit: 'degC',
        valid_value_units: ['degC', 'degF'],
        value_type: 'float',
      },
    }],
  }, {
    value_type: 'float',
    name: 'TT02',
    value: 23.4 + Math.random() * 2,
    value_unit: 'degC',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'TT03',
    value: 23.4 + Math.random() * 2,
    value_unit: 'degC',
    direction: 'output',
  }, {
    value_type: 'float',
    name: 'TT04',
    value: 23.4 + Math.random() * 2,
    value_unit: 'degC',
    direction: 'output',
  }, {
    value_type: 'string',
    name: 'Flow path',
    value: (getSeconds(Date.now()) % 10 < 3) ? 'Bypass' : (getSeconds(Date.now()) % 10 < 6) ? 'Prime with a long name' : undefined,
    direction: 'output',
  },
  {
    value_type: 'string',
    name: 'System State',
    value: systemState,
    direction: 'output',
  },
];


const runLogLines: RunLogLine[] = [
  {
    id: '1',
    start: sub(Date.now(), {days: 0, hours: 2, seconds: 20}).toISOString(),
    command: {
      command: 'Some Other Command',
      source: 'manually_entered',
    },
    start_values: [{
      name: 'Amazing float value',
      value: 1.43253342,
      value_type: 'float',
      value_unit: 'afv',
      direction: 'output',
    }],
    end_values: [],
    forcible: true,
    cancellable: false,
  }, {
    id: '2',
    start: sub(Date.now(), {days: 0, hours: 1, seconds: 10}).toISOString(),
    progress: 0.1234678,
    command: {
      command: 'Some Third Command With A Long Name',
      source: 'manually_entered',
    },
    start_values: [
      {
        name: 'Amazing float value',
        value: 999,
        value_type: 'float',
        value_unit: 'afv',
        direction: 'output',
      },
      {
        name: 'Best value',
        value: 19.99,
        value_type: 'float',
        value_unit: 'afv',
        direction: 'output',
      },
      {
        name: 'Such prices',
        value: 4299,
        value_type: 'float',
        value_unit: 'afv',
        direction: 'output',
      },
      {
        name: 'Very affordable',
        value: 0.99,
        value_type: 'float',
        value_unit: 'afv',
        direction: 'output',
      },
    ],
    end_values: [],
    forcible: true,
    cancellable: true,
  }, {
    id: '3',
    start: sub(Date.now(), {days: 1, hours: 3, seconds: 30}).toISOString(),
    end: sub(Date.now(), {days: 1, hours: 3}).toISOString(),
    command: {
      command: 'Supply the dakka',
      source: 'manually_entered',
    },
    start_values: [
      {
        name: 'Waaagh?',
        value: 'No waagh',
        value_type: 'string',
        direction: 'output',
      },
      {
        name: 'Dakka?',
        value: 'No dakka 🙁',
        value_type: 'string',
        direction: 'output',
      },
    ],
    end_values: [
      {
        name: 'Waaagh?',
        value: 'WAAAGH!',
        value_type: 'string',
        direction: 'output',
      },
      {
        name: 'Dakka?',
        value: 'DAKKA! 😀',
        value_type: 'string',
        direction: 'output',
      },
    ],
    forcible: false,
    cancellable: false,
    forced: false,
    cancelled: true,
  },
  {
    id: '4',
    start: sub(Date.now(), {days: 0, hours: 2, minutes: 23}).toISOString(),
    progress: 0.5123,
    command: {
      command: 'Some Command',
      source: 'manually_entered',
    },
    start_values: [{
      name: 'Amazing float value',
      value: 1.43253342,
      value_type: 'float',
      value_unit: 'afv',
      direction: 'output',
    }],
    end_values: [],
    forcible: false,
    cancellable: true,
  },
];


export const handlers = [
  http.get('/auth/config', () => {
    return HttpResponse.json<AuthConfig>({
      use_auth: false,
      client_id: 'fc7355bb-a6be-493f-90a1-cf57063f7948',
      authority_url: 'https://login.microsoftonline.com/fdfed7bd-9f6a-44a1-b694-6e39c468c150/v2.0',
    });
  }),

  http.get('/api/process_units', () => {
    return HttpResponse.json<ProcessUnit[]>(processUnits);
  }),

  http.get('/api/process_unit/:processUnitId', ({params}) => {
    const processUnit = processUnits.find(processUnit => processUnit.id.toString() === params['processUnitId']);
    if(processUnit === undefined) return new HttpResponse(undefined, {status: 404});
    return HttpResponse.json<ProcessUnit>(processUnit);
  }),

  http.get('/api/process_unit/:processUnitId/process_values', async () => {
    await delay();
    return HttpResponse.json<ProcessValue[]>(getProcessValues());
  }),

  http.get('/api/process_unit/:processUnitId/all_process_values', async () => {
    await delay();
    return HttpResponse.json<ProcessValue[]>(getProcessValues());
  }),

  http.get('/api/recent_runs/', () => {
    function getCompletedDate() {
      return sub(new Date(), {seconds: Math.random() * 1000000}).toISOString();
    }

    function getStartedDate() {
      return sub(new Date(), {hours: 2, seconds: Math.random() * 1000000}).toISOString();
    }

    return HttpResponse.json<RecentRun[]>([
      {
        engine_id: '1',
        run_id: crypto.randomUUID(),
        started_date: getStartedDate(),
        completed_date: getCompletedDate(),
        contributors: ['Eskild'],
        engine_computer_name: 'A computer name',
        engine_version: '0.0.1',
        engine_hardware_str: 'something',
        aggregator_version: '0.0.1',
        aggregator_computer_name: 'aggregator computer name',
        uod_author_name: 'someone',
        uod_author_email: 'someone@example.com',
        uod_filename: 'some_uod_file',
      },
      {
        engine_id: '2',
        run_id: crypto.randomUUID(),
        started_date: getStartedDate(),
        completed_date: getCompletedDate(),
        contributors: ['Eskild', 'Morten'],
        engine_computer_name: 'A computer name',
        engine_version: '0.0.1',
        engine_hardware_str: 'something',
        aggregator_version: '0.0.1',
        aggregator_computer_name: 'aggregator computer name',
        uod_author_name: 'someone',
        uod_author_email: 'someone@example.com',
        uod_filename: 'some_uod_file',
      },
      {
        engine_id: '3',
        run_id: crypto.randomUUID(),
        started_date: getStartedDate(),
        completed_date: getCompletedDate(),
        contributors: ['Eskild'],
        engine_computer_name: 'A computer name',
        engine_version: '0.0.1',
        engine_hardware_str: 'something',
        aggregator_version: '0.0.1',
        aggregator_computer_name: 'aggregator computer name',
        uod_author_name: 'someone',
        uod_author_email: 'someone@example.com',
        uod_filename: 'some_uod_file',
      },
      {
        engine_id: '4',
        run_id: crypto.randomUUID(),
        started_date: getStartedDate(),
        completed_date: getCompletedDate(),
        contributors: ['Eskild'],
        engine_computer_name: 'A computer name',
        engine_version: '0.0.1',
        engine_hardware_str: 'something',
        aggregator_version: '0.0.1',
        aggregator_computer_name: 'aggregator computer name',
        uod_author_name: 'someone',
        uod_author_email: 'someone@example.com',
        uod_filename: 'some_uod_file',
      },
    ]);
  }),

  http.post<PathParams, ExecutableCommand>('/api/process_unit/:unitId/execute_command', ({request}) => {
    request.json().then(executableCommand => {
      if(executableCommand.source === 'unit_button') {
        switch(executableCommand.command) {
          case 'Start':
            controlState.is_running = true;
            break;
          case 'Pause':
            controlState.is_paused = true;
            break;
          case 'Unpause':
            controlState.is_paused = false;
            break;
          case 'Hold':
            controlState.is_holding = true;
            break;
          case 'Unhold':
            controlState.is_holding = false;
            break;
          case 'Stop':
            controlState.is_running = false;
            break;
        }

        systemState = !controlState.is_running ? 'Stopped' :
                      controlState.is_paused ? 'Paused' :
                      controlState.is_holding ? 'Holding' :
                      'Running';
      }
    });
    return new HttpResponse();
  }),

  http.get('/api/process_unit/:unitId/process_diagram', () => {
    return HttpResponse.json({
      svg: '<!--suppress ALL --><svg xmlns:xlink="http://www.w3.org/1999/xlink" width="489" height="211" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 489 211"><defs/><g transform="translate(-214.00,-81.50)"><g transform="translate(233.260000,117.350000)" id="shape1"><path fill-rule="nonzero" fill="#ffffff" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0"/><path stroke="#000000" stroke-width="0.3199999928474426" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM10.0,10.0L10.0,.0M4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0" fill="none"/></g><g transform="translate(233.260000,183.850000)" id="shape2"><path fill-rule="nonzero" fill="#ffffff" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0"/><path stroke="#000000" stroke-width="0.3199999928474426" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM10.0,10.0L10.0,.0M4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0" fill="none"/></g><g transform="translate(355.000000,139.000000)" id="shape3"><path fill-rule="nonzero" fill="#ffffff" d="M.0,22.0C-0.0,9.8,9.8,.0,22.0,.0C34.2,-0.0,44.0,9.8,44.0,22.0C44.0,34.2,34.2,44.0,22.0,44.0C9.8,44.0,.0,34.2,.0,22.0z"/><path stroke="#000000" stroke-width="1" d="M.0,22.0C-0.0,9.8,9.8,.0,22.0,.0C34.2,-0.0,44.0,9.8,44.0,22.0C44.0,34.2,34.2,44.0,22.0,44.0C9.8,44.0,.0,34.2,.0,22.0zM8.8,39.6L44.0,22.0L8.8,4.4M.0,22.0L-11.0,22.0M44.0,22.0L55.0,22.0" fill="none"/></g><g transform="translate(253.260000,193.850000)" id="shape4"><path stroke="#191919" stroke-width="1" d="M.0,.0L58.7,.0L58.7,-32.9L84.7,-32.9" fill="none"/><path stroke-width="1" stroke="#191919" stroke-linecap="round" fill="#191919" d="M84.7,-35.9L90.7,-32.9L84.7,-29.9L84.7,-35.9"/></g><g transform="translate(253.260000,127.350000)" id="shape5"><path stroke="#191919" stroke-width="1" d="M.0,.0L58.7,.0L58.7,33.6L84.7,33.6" fill="none"/><path stroke-width="1" stroke="#191919" stroke-linecap="round" fill="#191919" d="M84.7,30.6L90.7,33.6L84.7,36.6L84.7,30.6"/></g><path fill-rule="nonzero" transform="translate(471.000000,176.000000)" stroke="#000000" stroke-width="1" fill="#ffffff" d="M.0,80.5C5.8,84.0,13.7,86.0,22.0,86.0C30.3,86.0,38.2,84.0,44.0,80.5L44.0,5.5C38.2,2.0,30.3,.0,22.0,.0C13.7,.0,5.8,2.0,.0,5.5L.0,80.5z" id="shape6"/><g transform="translate(410.000000,161.000000)" id="shape7"><path stroke="#191919" stroke-width="1" d="M.0,.0L83.0,.0L83.0,9.0" fill="none"/><path stroke-width="1" stroke="#191919" stroke-linecap="round" fill="#191919" d="M86.0,9.0L83.0,15.0L80.0,9.0L86.0,9.0"/></g><g transform="translate(436.000000,91.000000)" id="group8"><path fill-rule="nonzero" stroke="#000000" stroke-width="0.3199999928474426" fill="#ffffff" d="M.0,21.0C.0,9.4,9.4,.0,21.0,.0C32.6,.0,42.0,9.4,42.0,21.0C42.0,32.6,32.6,42.0,21.0,42.0C9.4,42.0,.0,32.6,.0,21.0z" id="shape9"/><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="19.1" x="11.5">FT</tspan></text></g><path transform="translate(457.000000,133.000000)" stroke="#191919" stroke-width="1" d="M.0,.0L.0,28.0" fill="none" id="shape10"/><g transform="translate(214.000000,94.500000)" id="shape11"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="40.5">VA01</tspan></text></g><g transform="translate(214.000000,161.000000)" id="shape12"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="40.5">VA02</tspan></text></g><g transform="translate(340.000000,176.000000)" id="shape13"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="4.0">PU01</tspan><tspan y="43.0" x="4.0">{{ PU01 </tspan><tspan y="59.0" x="4.0">Speed }}</tspan></text></g><g transform="translate(485.000000,81.500000)" id="shape14"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="4.0">FT01</tspan><tspan y="43.0" x="4.0">{{ FT01 Flow }}</tspan></text></g><g transform="translate(542.260000,219.000000)" id="group15"><path fill-rule="nonzero" stroke="#000000" stroke-width="0.3199999928474426" fill="#ffffff" d="M.0,21.0C.0,9.4,9.4,.0,21.0,.0C32.6,.0,42.0,9.4,42.0,21.0C42.0,32.6,32.6,42.0,21.0,42.0C9.4,42.0,.0,32.6,.0,21.0z" id="shape16"/><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="19.1" x="12.0">TT</tspan></text></g><path transform="translate(542.260000,240.000000)" stroke="#191919" stroke-width="1" d="M.0,.0L-27.0,.0" fill="none" id="shape17"/><g transform="translate(583.000000,238.500000)" id="shape18"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="4.0">TT01</tspan><tspan y="43.0" x="4.0">{{ TT01.PV }} 😀 {{ TT01.unit }}</tspan></text></g></g></svg>',
    });
  }),

  http.get('/api/process_unit/:unitId/command_examples', () => {
    return HttpResponse.json<CommandExample[]>([
      {
        name: 'Some Command',
        example: `SoMe\nmultiline\nexample\nwith\nmany\nlines\nto\ncause\nscrollbar\nto\nappear\nso\nit\ncan\nbe\ntested\nin\nthe\nbrowser`,
      }, {
        name: 'Some Other Command',
        example: `some other\n example`,
      }, {
        name: 'Some Advanced Command',
        example: `some\nAdvanced\nexample`,
      }, {
        name: 'Some Silly Command',
        example: `some\nSilly\nexample`,
      }, {
        name: 'Some Command, just to have more',
        example: `some\nexample, just to have more`,
      }, {
        name: 'Some Command with a very long name that probably should wrap somehow',
        example: `some very long example that maybe should wrap somehow`,
      }, {
        name: 'Yet another command',
        example: `yet another example`,
      }, {
        name: 'Yet another, another command',
        example: `yet another, another example`,
      },
    ]);
  }),

  http.get('/api/process_unit/:unitId/run_log', async () => {
    await delay();
    return HttpResponse.json<RunLog>({
      lines: runLogLines,
    });
  }),

  http.get('/api/process_unit/:unitId/method-and-state', () => {
    const lines = [
      {id: 'a', content: '{'},
      {id: 'b', content: ' "watch": "some condition",'},
      {id: 'c', content: ' "some unrun": "line",'},
      {id: 'd', content: ' "injected": "line",'},
      {id: 'e', content: ' "another": "line",'},
      {id: 'f', content: ' "yet another": "line"'},
      {id: 'g', content: '}'},
    ];
    const result = HttpResponse.json<MethodAndState>({
      method: {lines: lines},
      state: {
        started_line_ids: startedLines.map(no => (no + 9).toString(36)),
        executed_line_ids: executedLines.map(no => (no + 9).toString(36)),
        injected_line_ids: ['d'],
      },
    });
    const lastExecutedLine = executedLines.at(-1) ?? 0;
    if(lastExecutedLine < lines.length) executedLines.push(lastExecutedLine + 1);
    return result;
  }),

  http.post('/api/process_unit/:unitId/method', () => {
    return new HttpResponse();
  }),

  http.get('/api/process_unit/:unitId/plot_configuration', () => {
    return HttpResponse.json<PlotConfiguration>({
      x_axis_process_value_names: ['Timestamp', 'Timestamp2'],
      process_value_names_to_annotate: ['Flow path'],
      color_regions: [{
        process_value_name: 'Flow path',
        value_color_map: {
          'Bypass': '#3366dd33',
          'Prime with a long name': '#33aa6633',
        },
      }],
      sub_plots: [
        {
          ratio: 1.5,
          axes: [
            {
              label: 'Red',
              process_value_names: ['PU01 Speed', 'PU02 Speed', 'PU03 Speed', 'PU04 Speed', 'PU05 Speed', 'PU06 Speed'],
              y_max: 126,
              y_min: 119,
              color: '#ff3333',
            },
            {
              label: 'Blue',
              process_value_names: ['TT01'],
              y_max: 26,
              y_min: 20,
              color: '#1144ff',
            },
            {
              label: 'Teal label',
              process_value_names: ['TT02'],
              y_max: 32,
              y_min: 22,
              color: '#43c5b7',
            },
          ],
        },
        {
          ratio: 1,
          axes: [{
            label: 'Green',
            process_value_names: ['TT03'],
            y_max: 26,
            y_min: 20,
            color: '#33ff33',
          }, {
            label: 'orange',
            process_value_names: ['TT04'],
            y_max: 29,
            y_min: 19,
            color: '#ff8000',
          }],
        },
      ],
    });
  }),

  http.get('/api/process_unit/:unitId/plot_log', () => {
    const noOfValues = 90;
    const attachTickTime = (value: object, index: number) => ({...value, tick_time: (Date.now() - (noOfValues - index)) / 1000});
    return HttpResponse.json<PlotLog>({
      entries: {
        'Timestamp': {
          value_type: 'int',
          name: 'Timestamp',
          values: new Array(noOfValues).fill(undefined).map(
            (_, index) => ({value: new Date().valueOf() - 1000 * (noOfValues - index)}))
            .map(attachTickTime),
        },
        'Timestamp2': {
          value_type: 'int',
          name: 'Timestamp2',
          values: new Array(noOfValues).fill(undefined).map(
            (_, index) => ({value: new Date().valueOf() - 1000 * (noOfValues - index) + 1000000000000}))
            .map(attachTickTime),
        },
        'PU01 Speed': {
          value_type: 'float',
          name: 'PU01 Speed',
          values: new Array(noOfValues).fill({value: 120}).map(attachTickTime),
          value_unit: '%',
        },
        'PU02 Speed': {
          value_type: 'float',
          name: 'PU02 Speed',
          values: new Array(noOfValues).fill({value: 121}).map(attachTickTime),
          value_unit: '%',
        },
        'PU03 Speed': {
          value_type: 'float',
          name: 'PU03 Speed',
          values: new Array(noOfValues).fill({value: 122}).map(attachTickTime),
          value_unit: '%',
        },
        'PU04 Speed': {
          value_type: 'float',
          name: 'PU04 Speed',
          values: new Array(noOfValues).fill({value: 123}).map(attachTickTime),
          value_unit: '%',
        },
        'PU05 Speed': {
          value_type: 'float',
          name: 'PU05 Speed',
          values: new Array(noOfValues).fill({value: 124}).map(attachTickTime),
          value_unit: '%',
        },
        'PU06 Speed': {
          value_type: 'float',
          name: 'PU06 Speed',
          values: new Array(noOfValues).fill({value: 125}).map(attachTickTime),
          value_unit: '%',
        },
        'FT01 Flow': {
          value_type: 'float',
          name: 'FT01 Flow',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 123 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'L/h',
        },
        'TT01': {
          value_type: 'float',
          name: 'TT01',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'TT02': {
          value_type: 'float',
          name: 'TT02',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'TT03': {
          value_type: 'float',
          name: 'TT03',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'TT04': {
          value_type: 'float',
          name: 'TT04',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'Flow path': {
          value_type: 'string',
          name: 'Flow path',
          values: new Array(noOfValues).fill(undefined).map((_, index) =>
            ({value: (index % 9 < 3) ? 'Bypass' : (index % 9 < 6) ? 'Prime with a long name' : undefined}),
          ).map(attachTickTime),
        },
      },
    });
  }),

  http.get('/api/process_unit/:unitId/control_state', () => {
    return HttpResponse.json<ControlState>(controlState);
  }),

  http.get('/api/process_unit/:unitId/error_log', () => {
    return HttpResponse.json<AggregatedErrorLog>({
      entries: [
        {
          created_time: sub(new Date(), {minutes: 5, seconds: Math.random() * 50}).toISOString(),
          severity: 'warning',
          message: 'Just a warning',
          occurrences: 2,
        },
        {
          created_time: sub(new Date(), {minutes: 5, seconds: Math.random() * 50}).toISOString(),
          severity: 'warning',
          message: 'Just another warning',
          occurrences: 1,
        },
        {
          created_time: sub(new Date(), {seconds: Math.random() * 50}).toISOString(),
          severity: 'error',
          message: 'Oh no! An error!',
          occurrences: 100,
        },
      ],
    });
  }),


  /***************
   * RECENT RUNS *
   ***************/

  http.get('/api/recent_runs/:id/method-and-state', async () => {
    await delay();
    return HttpResponse.json<MethodAndState>({
      method: {
        lines: [
          {id: 'a', content: '{'},
          {id: 'b', content: ' "some key": "some value",'},
          {id: 'c', content: ' "injected": "line",'},
          {id: 'd', content: ' "watch": "some condition",'},
          {id: 'e', content: ' "an unrun": "line",'},
          {id: 'f', content: ' "another unrun": "line"'},
          {id: 'g', content: '}'},
        ],
      },
      state: {
        started_line_ids: ['d'],
        executed_line_ids: ['a', 'b', 'c', 'g'],
        injected_line_ids: ['c'],
      },
    });
  }),

  http.get('/api/recent_runs/:id/run_log', async () => {
    await delay();
    return HttpResponse.json<RunLog>({
      lines: [
        {
          id: '1',
          start: sub(Date.now(), {days: 0, hours: 2, seconds: 20}).toISOString(),
          end: sub(Date.now(), {days: 0, hours: 1, seconds: 20}).toISOString(),
          command: {
            command: 'Some Other Command',
            source: 'manually_entered',
          },
          start_values: [{
            name: 'Amazing float value',
            value: 1.43253342,
            value_type: 'float',
            value_unit: 'afv',
            direction: 'output',
          }],
          end_values: [],
        }, {
          id: '2',
          start: sub(Date.now(), {days: 0, hours: 1, seconds: 10}).toISOString(),
          end: sub(Date.now(), {days: 0, hours: 0, seconds: 10}).toISOString(),
          command: {
            command: 'Some Third Command',
            source: 'manually_entered',
          },
          start_values: [
            {
              name: 'Amazing float value',
              value: 999,
              value_type: 'float',
              value_unit: 'afv',
              direction: 'output',
            },
            {
              name: 'Best value',
              value: 19.99,
              value_type: 'float',
              value_unit: 'afv',
              direction: 'output',
            },
            {
              name: 'Such prices',
              value: 4299,
              value_type: 'float',
              value_unit: 'afv',
              direction: 'output',
            },
            {
              name: 'Very affordable',
              value: 0.99,
              value_type: 'float',
              value_unit: 'afv',
              direction: 'output',
            },
          ],
          end_values: [],
          forcible: false,
          cancellable: false,
        }, {
          id: '3',
          start: sub(Date.now(), {days: 1, hours: 3, seconds: 30}).toISOString(),
          end: sub(Date.now(), {days: 1, hours: 3}).toISOString(),
          command: {
            command: 'Supply the dakka',
            source: 'manually_entered',
          },
          start_values: [
            {
              name: 'Waaagh?',
              value: 'No waagh',
              value_type: 'string',
              direction: 'output',
            },
            {
              name: 'Dakka?',
              value: 'No dakka 🙁',
              value_type: 'string',
              direction: 'output',
            },
          ],
          end_values: [
            {
              name: 'Waaagh?',
              value: 'WAAAGH!',
              value_type: 'string',
              direction: 'output',
            },
            {
              name: 'Dakka?',
              value: 'DAKKA! 😀',
              value_type: 'string',
              direction: 'output',
            },
          ],
        },
      ],
    });
  }),

  http.get('/api/recent_runs/:id/error_log', () => {
    return HttpResponse.json<AggregatedErrorLog>({
      entries: [
        {
          created_time: sub(new Date(), {minutes: 5, seconds: Math.random() * 500}).toISOString(),
          severity: 'warning',
          message: 'Just a warning',
        },
        {
          created_time: sub(new Date(), {seconds: Math.random() * 500}).toISOString(),
          severity: 'error',
          message: 'Oh no! An error!',
        },
      ],
    });
  }),

  http.get('/api/recent_runs/:id', ({params}) => {
    return HttpResponse.json<RecentRun>({
      started_date: sub(new Date(), {hours: 3, minutes: 22, seconds: 11}).toISOString(),
      completed_date: sub(new Date(), {hours: 1}).toISOString(),
      contributors: ['Morten', 'Eskild'],
      engine_id: 'A process unit id',
      run_id: crypto.randomUUID(),
      engine_computer_name: 'A computer name',
      engine_version: '0.0.1',
      engine_hardware_str: 'something',
      aggregator_version: '0.0.1',
      aggregator_computer_name: 'aggregator computer name',
      uod_author_name: 'someone',
      uod_author_email: 'someone@example.com',
      uod_filename: 'some_uod_file',
    });
  }),


  http.get('/api/recent_runs/:id/plot_configuration', () => {
    return HttpResponse.json<PlotConfiguration>({
      x_axis_process_value_names: ['Timestamp', 'Timestamp2'],
      process_value_names_to_annotate: ['Flow path'],
      color_regions: [{
        process_value_name: 'Flow path',
        value_color_map: {
          'Bypass': '#3366dd33',
          'Prime with a long name': '#33aa6633',
        },
      }],
      sub_plots: [
        {
          ratio: 1.5,
          axes: [
            {
              label: 'Red',
              process_value_names: ['PU01 Speed', 'PU02 Speed', 'PU03 Speed', 'PU04 Speed', 'PU05 Speed', 'PU06 Speed'],
              y_max: 126,
              y_min: 119,
              color: '#ff3333',
            },
            {
              label: 'Blue',
              process_value_names: ['TT01'],
              y_max: 26,
              y_min: 20,
              color: '#1144ff',
            },
            {
              label: 'Teal label',
              process_value_names: ['TT02'],
              y_max: 32,
              y_min: 22,
              color: '#43c5b7',
            },
          ],
        },
        {
          ratio: 1,
          axes: [{
            label: 'Green',
            process_value_names: ['TT03'],
            y_max: 26,
            y_min: 20,
            color: '#33ff33',
          }, {
            label: 'orange',
            process_value_names: ['TT04'],
            y_max: 29,
            y_min: 19,
            color: '#ff8000',
          }],
        },
      ],
    });
  }),

  http.get('/api/recent_runs/:id/plot_log', () => {
    const noOfValues = 90;
    const attachTickTime = (value: object, index: number) => ({...value, tick_time: (Date.now() - (noOfValues - index)) / 1000});
    return HttpResponse.json<PlotLog>({
      entries: {
        'Timestamp': {
          value_type: 'int',
          name: 'Timestamp',
          values: new Array(noOfValues).fill(undefined).map(
            (_, index) => ({value: new Date().valueOf() - 1000 * (noOfValues - index)}))
            .map(attachTickTime),
        },
        'Timestamp2': {
          value_type: 'int',
          name: 'Timestamp2',
          values: new Array(noOfValues).fill(undefined).map(
            (_, index) => ({value: new Date().valueOf() - 1000 * (noOfValues - index) + 1000000000000}))
            .map(attachTickTime),
        },
        'PU01 Speed': {
          value_type: 'float',
          name: 'PU01 Speed',
          values: new Array(noOfValues).fill({value: 120}).map(attachTickTime),
          value_unit: '%',
        },
        'PU02 Speed': {
          value_type: 'float',
          name: 'PU02 Speed',
          values: new Array(noOfValues).fill({value: 121}).map(attachTickTime),
          value_unit: '%',
        },
        'PU03 Speed': {
          value_type: 'float',
          name: 'PU03 Speed',
          values: new Array(noOfValues).fill({value: 122}).map(attachTickTime),
          value_unit: '%',
        },
        'PU04 Speed': {
          value_type: 'float',
          name: 'PU04 Speed',
          values: new Array(noOfValues).fill({value: 123}).map(attachTickTime),
          value_unit: '%',
        },
        'PU05 Speed': {
          value_type: 'float',
          name: 'PU05 Speed',
          values: new Array(noOfValues).fill({value: 124}).map(attachTickTime),
          value_unit: '%',
        },
        'PU06 Speed': {
          value_type: 'float',
          name: 'PU06 Speed',
          values: new Array(noOfValues).fill({value: 125}).map(attachTickTime),
          value_unit: '%',
        },
        'FT01 Flow': {
          value_type: 'float',
          name: 'FT01 Flow',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 123 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'L/h',
        },
        'TT01': {
          value_type: 'float',
          name: 'TT01',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'TT02': {
          value_type: 'float',
          name: 'TT02',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'TT03': {
          value_type: 'float',
          name: 'TT03',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'TT04': {
          value_type: 'float',
          name: 'TT04',
          values: new Array(noOfValues).fill(undefined).map(() => ({value: 23.4 + Math.random() * 2})).map(attachTickTime),
          value_unit: 'degC',
        },
        'Flow path': {
          value_type: 'string',
          name: 'Flow path',
          values: new Array(noOfValues).fill(undefined).map((_, index) =>
            ({value: (index % 9 < 3) ? 'Bypass' : (index % 9 < 6) ? 'Prime with a long name' : undefined}),
          ).map(attachTickTime),
        },
      },
    });
  }),

  http.get('/api/recent_runs/:id/csv_file', ({params}) => {
    const csvContent = `Some;CSV;File
123;456;789`;
    return new HttpResponse(csvContent, {
      headers: {
        'Content-Length': csvContent.length.toString(),
        'Content-Type': 'text/csv',
        'Content-Disposition': `attachment;filename="RecentRun-${params['id']}.csv"`,
      },
    });
  }),

  http.get('/api/recent_runs/:id/csv_json', ({params}) => {
    return HttpResponse.json<RecentRunCsv>({
      filename: `P2 - A process unit name - ${format(new Date(), 'yyyy-MM-dd_HH-mm-ss')}.csv`,
      csv_content: `# Recent Run Id:;${params['id']}
# Process Unit Name:;A process unit name
# Starting Time:;${new Date().toISOString()}
# Ending Time:;${new Date().toISOString()}
# Contributors:;Eskild;Morten

Some;Csv;Data
123;456;789
123;456;789
123;456;789`,
    });
  }),

  http.post('/api/process_unit/:unitId/run_log/force_line/:lineId', ({params}) => {
    const line = runLogLines.find(runLogLine => runLogLine.id.toString() === params['lineId']);
    if(line !== undefined) {
      line.forced = true;
      line.forcible = false;
      line.cancellable = false;
      line.end = new Date().toISOString();
    }
    return new HttpResponse();
  }),

  http.post('/api/process_unit/:unitId/run_log/cancel_line/:lineId', ({params}) => {
    const line = runLogLines.find(runLogLine => runLogLine.id.toString() === params['lineId']);
    if(line !== undefined) {
      line.cancelled = true;
      line.cancellable = false;
      line.forcible = false;
      line.end = new Date().toISOString();
    }
    return new HttpResponse();
  }),
];
