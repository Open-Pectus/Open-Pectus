import { sub } from 'date-fns';
import { rest } from 'msw';
import {
  BatchJob,
  CommandExample,
  CommandSource,
  InProgress,
  NotOnline,
  PlotConfiguration,
  ProcessUnit,
  ProcessValue,
  ProcessValueCommandChoiceValue,
  ProcessValueCommandFreeTextValue,
  ProcessValueType,
  Ready,
  RunLog,
  UserRole,
} from '../app/api';

const processUnits: ProcessUnit[] = [
  {
    name: 'Some unit',
    id: 'some_unit',
    location: 'Some place',
    runtime_msec: 59999,
    state: {
      state: InProgress.state.IN_PROGRESS,
      progress_pct: 30,
    },
    current_user_role: UserRole.ADMIN,
  },
  {
    name: 'Some other unit with a long title',
    id: 'some_other_unit',
    location: 'Some place else',
    runtime_msec: 456498,
    state: {
      state: Ready.state.READY,
    },
    current_user_role: UserRole.ADMIN,
  },
  {
    name: 'Some third unit',
    id: 'some_third_unit',
    location: 'Some third place',
    runtime_msec: 12365,
    state: {
      state: NotOnline.state.NOT_ONLINE,
      last_seen_date: new Date().toJSON(),
    },
    current_user_role: UserRole.ADMIN,
  },
  {
    name: 'A fourth for linebreak',
    id: 'a_fourth',
    location: 'Narnia',
    runtime_msec: 85264,
    state: {
      state: NotOnline.state.NOT_ONLINE,
      last_seen_date: new Date().toJSON(),
    },
    current_user_role: UserRole.VIEWER,
  },
];


export const handlers = [
  rest.get('/api/process_units', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json<ProcessUnit[]>(processUnits),
    );
  }),

  rest.get('/api/process_unit/:processUnitId', (req, res, ctx) => {
    const processUnit = processUnits.find(processUnit => processUnit.id.toString() === req.params['processUnitId']);
    if(processUnit === undefined) return res(ctx.status(404));
    return res(
      ctx.status(200),
      ctx.json<ProcessUnit>(processUnit),
    );
  }),

  rest.get('/api/process_unit/:processUnitId/process_values', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.delay(),
      ctx.json<ProcessValue[]>([
        {
          value_type: ProcessValueType.FLOAT,
          name: 'PU01 Speed',
          value: 123 + Math.random() * 2,
          value_unit: '%',
        }, {
          value_type: ProcessValueType.STRING,
          name: 'Some other Process Value',
          value: 'So very valuable',
          commands: [
            {command: 'some_command', name: 'Some Command'},
            {command: 'some_other_command', name: 'Some Other Command'},
          ],
        }, {
          value_type: ProcessValueType.INT,
          name: 'A value with unit',
          value: 1000,
          value_unit: 'm',
          commands: [
            {
              command: 'fdsa', name: 'fdsa', value: {
                value: 1000,
                value_type: ProcessValueType.INT,
                value_unit: 'm',
                valid_value_units: ['m', 'cm', 'mm', 'km'],
              },
            },
          ],
        }, {
          value_type: ProcessValueType.STRING,
          name: 'Many Data',
          value: 'HANDLE IT',
        }, {
          value_type: ProcessValueType.FLOAT,
          name: 'FT01 Flow',
          value: 123 + Math.random() * 2,
          value_unit: 'L/h',
          commands: [
            {
              command: 'fdsafsa',
              name: 'Set',
              value: {
                value: 123 + Math.random() * 2,
                value_unit: 'L/h',
                valid_value_units: ['L/h', 'm3/h', 'L/m', 'm3/m'],
                value_type: ProcessValueType.FLOAT,
              },
            },
          ],
        }, {
          value_type: ProcessValueType.STRING,
          name: 'Writable text',
          value: 'VaLuE',
          commands: [{
            name: 'jiojio',
            command: 'jiojio',
            value: {
              value: 'Writable text',
              value_type: ProcessValueCommandFreeTextValue.value_type.STRING,
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
              value_type: ProcessValueType.INT,
            },
          }, {
            name: 'choice',
            command: 'choice',
            value: {
              value_type: ProcessValueCommandChoiceValue.value_type.CHOICE,
              value: 'first',
              options: ['first', 'second', 'third'],
            },
          }],
        }, {
          value_type: ProcessValueType.FLOAT,
          name: 'TT01',
          value: 23.4 + Math.random() * 2,
          value_unit: 'degC',
          commands: [{
            name: 'Set target temperature',
            command: 'set_target_temperature',
            value: {
              value: 23.4 + Math.random() * 2,
              value_unit: 'degC',
              valid_value_units: ['degC', 'degF'],
              value_type: ProcessValueType.FLOAT,
            },
          }],
        },
      ]),
    );
  }),

  rest.get('/api/recent_batch_jobs', (req, res, ctx) => {
    function getCompletedDate() {
      return sub(new Date(), {seconds: Math.random() * 1000000}).toISOString();
    }

    return res(
      ctx.status(200),
      ctx.json<BatchJob[]>([
        {
          id: 1,
          unit_id: '1',
          unit_name: 'Some Name 1 that is very long, and way longer than it should be.',
          completed_date: getCompletedDate(),
          contributors: ['Eskild'],
        },
        {id: 2, unit_id: '2', unit_name: 'Some Name 2', completed_date: getCompletedDate(), contributors: ['Eskild', 'Morten']},
        {id: 3, unit_id: '3', unit_name: 'Some Name 3', completed_date: getCompletedDate(), contributors: ['Eskild']},
        {id: 4, unit_id: '4', unit_name: 'Some Name 4', completed_date: getCompletedDate(), contributors: ['Eskild']},
      ]),
    );
  }),

  rest.post('/api/process_unit/:unitId/execute_command', (req, res, context) => {
    return res(
      context.status(200),
    );
  }),

  rest.get('/api/process_unit/:unitId/process_diagram', (req, res, context) => {
    return res(
      context.status(200),
      context.json({
        svg: '<svg xmlns:xlink="http://www.w3.org/1999/xlink" width="489" height="211" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 489 211"><defs/><g transform="translate(-214.00,-81.50)"><g transform="translate(233.260000,117.350000)" id="shape1"><path fill-rule="nonzero" fill="#ffffff" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0"/><path stroke="#000000" stroke-width="0.3199999928474426" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM10.0,10.0L10.0,.0M4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0" fill="none"/></g><g transform="translate(233.260000,183.850000)" id="shape2"><path fill-rule="nonzero" fill="#ffffff" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0"/><path stroke="#000000" stroke-width="0.3199999928474426" d="M.0,5.0L.0,15.0L20.0,5.0L20.0,15.0L.0,5.0zM10.0,10.0L10.0,.0M4.0,.0L16.0,.0L16.0,-12.0L4.0,-12.0L4.0,.0" fill="none"/></g><g transform="translate(355.000000,139.000000)" id="shape3"><path fill-rule="nonzero" fill="#ffffff" d="M.0,22.0C-0.0,9.8,9.8,.0,22.0,.0C34.2,-0.0,44.0,9.8,44.0,22.0C44.0,34.2,34.2,44.0,22.0,44.0C9.8,44.0,.0,34.2,.0,22.0z"/><path stroke="#000000" stroke-width="1" d="M.0,22.0C-0.0,9.8,9.8,.0,22.0,.0C34.2,-0.0,44.0,9.8,44.0,22.0C44.0,34.2,34.2,44.0,22.0,44.0C9.8,44.0,.0,34.2,.0,22.0zM8.8,39.6L44.0,22.0L8.8,4.4M.0,22.0L-11.0,22.0M44.0,22.0L55.0,22.0" fill="none"/></g><g transform="translate(253.260000,193.850000)" id="shape4"><path stroke="#191919" stroke-width="1" d="M.0,.0L58.7,.0L58.7,-32.9L84.7,-32.9" fill="none"/><path stroke-width="1" stroke="#191919" stroke-linecap="round" fill="#191919" d="M84.7,-35.9L90.7,-32.9L84.7,-29.9L84.7,-35.9"/></g><g transform="translate(253.260000,127.350000)" id="shape5"><path stroke="#191919" stroke-width="1" d="M.0,.0L58.7,.0L58.7,33.6L84.7,33.6" fill="none"/><path stroke-width="1" stroke="#191919" stroke-linecap="round" fill="#191919" d="M84.7,30.6L90.7,33.6L84.7,36.6L84.7,30.6"/></g><path fill-rule="nonzero" transform="translate(471.000000,176.000000)" stroke="#000000" stroke-width="1" fill="#ffffff" d="M.0,80.5C5.8,84.0,13.7,86.0,22.0,86.0C30.3,86.0,38.2,84.0,44.0,80.5L44.0,5.5C38.2,2.0,30.3,.0,22.0,.0C13.7,.0,5.8,2.0,.0,5.5L.0,80.5z" id="shape6"/><g transform="translate(410.000000,161.000000)" id="shape7"><path stroke="#191919" stroke-width="1" d="M.0,.0L83.0,.0L83.0,9.0" fill="none"/><path stroke-width="1" stroke="#191919" stroke-linecap="round" fill="#191919" d="M86.0,9.0L83.0,15.0L80.0,9.0L86.0,9.0"/></g><g transform="translate(436.000000,91.000000)" id="group8"><path fill-rule="nonzero" stroke="#000000" stroke-width="0.3199999928474426" fill="#ffffff" d="M.0,21.0C.0,9.4,9.4,.0,21.0,.0C32.6,.0,42.0,9.4,42.0,21.0C42.0,32.6,32.6,42.0,21.0,42.0C9.4,42.0,.0,32.6,.0,21.0z" id="shape9"/><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="19.1" x="11.5">FT</tspan></text></g><path transform="translate(457.000000,133.000000)" stroke="#191919" stroke-width="1" d="M.0,.0L.0,28.0" fill="none" id="shape10"/><g transform="translate(214.000000,94.500000)" id="shape11"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="40.5">VA01</tspan></text></g><g transform="translate(214.000000,161.000000)" id="shape12"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="40.5">VA02</tspan></text></g><g transform="translate(340.000000,176.000000)" id="shape13"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="4.0">PU01</tspan><tspan y="43.0" x="4.0">{{ PU01 </tspan><tspan y="59.0" x="4.0">Speed }}</tspan></text></g><g transform="translate(485.000000,81.500000)" id="shape14"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="4.0">FT01</tspan><tspan y="43.0" x="4.0">{{ FT01 Flow }}</tspan></text></g><g transform="translate(542.260000,219.000000)" id="group15"><path fill-rule="nonzero" stroke="#000000" stroke-width="0.3199999928474426" fill="#ffffff" d="M.0,21.0C.0,9.4,9.4,.0,21.0,.0C32.6,.0,42.0,9.4,42.0,21.0C42.0,32.6,32.6,42.0,21.0,42.0C9.4,42.0,.0,32.6,.0,21.0z" id="shape16"/><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="19.1" x="12.0">TT</tspan></text></g><path transform="translate(542.260000,240.000000)" stroke="#191919" stroke-width="1" d="M.0,.0L-27.0,.0" fill="none" id="shape17"/><g transform="translate(583.000000,238.500000)" id="shape18"><text style="fill:#191919;font-family:Arial;font-size:12.00pt" xml:space="preserve"><tspan y="24.0" x="4.0">TT01</tspan><tspan y="43.0" x="4.0">{{ TT01.PV }} 😀 {{ TT01.unit }}</tspan></text></g></g></svg>',
      }),
    );
  }),

  rest.get('/api/process_unit/:unitId/command_examples', (req, res, context) => {
    return res(
      context.status(200),
      context.json<CommandExample[]>([
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
      ]),
    );
  }),

  rest.get('/api/process_unit/:unitId/run_log', (req, res, context) => {
    return res(
      context.status(200),
      context.json<RunLog>({
        lines: [
          {
            id: 1,
            start: sub(Date.now(), {days: 0, hours: 2, seconds: 20}).toISOString(),
            command: {
              command: 'Some Other Command',
              source: CommandSource.MANUALLY_ENTERED,
            },
            start_values: [{
              name: 'Amazing float value',
              value: 1.43253342,
              value_type: ProcessValueType.FLOAT,
              value_unit: 'afv',
            }],
            end_values: [],
          }, {
            id: 2,
            start: sub(Date.now(), {days: 0, hours: 1, seconds: 10}).toISOString(),
            progress: 0.66,
            command: {
              command: 'Some Third Command',
              source: CommandSource.MANUALLY_ENTERED,
            },
            start_values: [
              {name: 'Amazing float value', value: 999, value_type: ProcessValueType.FLOAT, value_unit: 'afv'},
              {name: 'Best value', value: 19.99, value_type: ProcessValueType.FLOAT, value_unit: 'afv'},
              {name: 'Such prices', value: 4299, value_type: ProcessValueType.FLOAT, value_unit: 'afv'},
              {name: 'Very affordable', value: 0.99, value_type: ProcessValueType.FLOAT, value_unit: 'afv'},
            ],
            end_values: [],
          }, {
            id: 3,
            start: sub(Date.now(), {days: 1, hours: 3, seconds: 30}).toISOString(),
            end: sub(Date.now(), {days: 1, hours: 3}).toISOString(),
            command: {
              command: 'Supply the dakka',
              source: CommandSource.MANUALLY_ENTERED,
            },
            start_values: [
              {name: 'Waaagh?', value: 'No waagh', value_type: ProcessValueType.STRING},
              {name: 'Dakka?', value: 'No dakka 🙁', value_type: ProcessValueType.STRING},
            ],
            end_values: [
              {name: 'Waaagh?', value: 'WAAAGH!', value_type: ProcessValueType.STRING},
              {name: 'Dakka?', value: 'DAKKA! 😀', value_type: ProcessValueType.STRING},
            ],
          },
        ],
      }),
    );
  }),

  rest.get('/api/process_unit/:unitId/method', (req, res, context) => {
    return res(
      context.status(200),
      context.json<string>(`{
"some key": "some value",
"injected": "line",
"another key": "another value",
"another injected": "line"
}`),
    );
  }),

  rest.get('/api/process_unit/:unitId/plot_configuration', (req, res, context) => {
    return res(
      context.status(200),
      context.json<PlotConfiguration>({
        color_regions: [],
        sub_plots: [
          {
            ratio: 1,
            axes: [
              {
                label: 'some Label',
                process_value_names: ['PU01 Speed', 'FT01 Flow'],
                y_max: 126,
                y_min: 123,
                color: '#ff3333',
              }, {
                label: 'Label label',
                process_value_names: ['TT01'],
                y_max: 26,
                y_min: 20,
                color: '#1144ff',
              },
            ],
          },
          {
            ratio: 1,
            axes: [{
              label: 'some other label',
              process_value_names: ['TT01'],
              y_max: 26,
              y_min: 20,
              color: '#33ff33',
            }],
          },
        ],
      }),
    );
  }),
];
