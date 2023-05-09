import { sub } from 'date-fns';
import { rest } from 'msw';
import { BatchJob, InProgress, NotOnline, ProcessUnit, ProcessValue, ProcessValueType, Ready } from '../app/api';

const processUnits = [
  {
    name: 'Some unit',
    id: 1,
    location: 'Some place',
    runtime_msec: 59999,
    state: {
      state: InProgress.state.IN_PROGRESS,
      progress_pct: 30,
    },
  },
  {
    name: 'Some other unit with a long title',
    id: 2,
    location: 'Some place else',
    runtime_msec: 456498,
    state: {
      state: Ready.state.READY,
    },
  },
  {
    name: 'Some third unit',
    id: 3,
    location: 'Some third place',
    runtime_msec: 12365,
    state: {
      state: NotOnline.state.NOT_ONLINE,
      last_seen_date: new Date().toJSON(),
    },
  },
  {
    name: 'A fourth for linebreak',
    id: 4,
    location: 'Narnia',
    runtime_msec: 85264,
    state: {
      state: NotOnline.state.NOT_ONLINE,
      last_seen_date: new Date().toJSON(),
    },
  },
];


export const handlers = [
  rest.get('/process_units', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json<ProcessUnit[]>(processUnits),
    );
  }),

  rest.get('/process_unit/:processUnitId', (req, res, ctx) => {
    const processUnit = processUnits.find(processUnit => processUnit.id.toString() === req.params['processUnitId']);
    if(processUnit === undefined) return res(ctx.status(404));
    return res(
      ctx.status(200),
      ctx.json<ProcessUnit>(processUnit),
    );
  }),

  rest.get('/process_unit/:processUnitId/process_values', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json<ProcessValue[]>([
        {
          value_type: ProcessValueType.INT,
          name: 'some process value',
          value: 123,
          writable: false,
        }, {
          value_type: ProcessValueType.STRING,
          name: 'Some other Process Value',
          value: 'So very valuable',
          writable: false,
          commands: [
            {command: 'some_command', name: 'Some Command'},
            {command: 'some_other_command', name: 'Some Other Command'},
          ],
        }, {
          value_type: ProcessValueType.INT,
          name: 'A value with unit',
          value: 1000,
          value_unit: 'm',
          valid_value_units: ['m', 'cm', 'mm', 'km'],
          writable: true,
        }, {
          value_type: ProcessValueType.STRING,
          name: 'Many Data',
          value: 'HANDLE IT',
          writable: false,
        }, {
          value_type: ProcessValueType.INT,
          name: 'A writable value',
          value: 123,
          writable: true,
        }, {
          value_type: ProcessValueType.STRING,
          name: 'A writable text value',
          value: 'VaLuE',
          writable: true,
        },
      ]),
    );
  }),

  rest.get('/recent_batch_jobs', (req, res, ctx) => {
    function getCompletedDate() {
      return sub(new Date(), {seconds: Math.random() * 1000000}).toISOString();
    }

    return res(
      ctx.status(200),
      ctx.json<BatchJob[]>([
        {
          id: 1,
          unit_id: 1,
          unit_name: 'Some Name 1 that is very long, and way longer than it should be.',
          completed_date: getCompletedDate(),
          contributors: ['Eskild'],
        },
        {id: 2, unit_id: 2, unit_name: 'Some Name 2', completed_date: getCompletedDate(), contributors: ['Eskild', 'Morten']},
        {id: 3, unit_id: 3, unit_name: 'Some Name 3', completed_date: getCompletedDate(), contributors: ['Eskild']},
        {id: 4, unit_id: 4, unit_name: 'Some Name 4', completed_date: getCompletedDate(), contributors: ['Eskild']},
      ]),
    );
  }),

  rest.post('/process_unit/:unitId/process_value/:processValueName', (req, res, context) => {
    return res(
      context.status(200),
    );
  }),
];
