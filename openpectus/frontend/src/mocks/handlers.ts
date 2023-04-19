import { rest } from 'msw';
import { ProcessUnit, ProcessUnitStateEnum } from '../app/api';

export const handlers = [
  rest.get('/process_units', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json<ProcessUnit[]>([{
        name: 'Some unit',
        id: 1,
        state: {
          state: ProcessUnitStateEnum.InProgress,
          progress_pct: 30,
          last_seen_date: new Date().toJSON(),
        },
      }]),
    );
  }),

  rest.get('https://fonts.googleapis.com/css2?family=Open+Sans:wght@200..900', (req, res, ctx) => {
    return req.passthrough();
  }),
];
