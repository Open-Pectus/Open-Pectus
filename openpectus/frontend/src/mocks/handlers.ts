import { rest } from 'msw';
import { ProcessUnit, ProcessUnitStateEnum } from '../app/api';

export const handlers = [
  rest.get('/process_units', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json<ProcessUnit[]>([
        {
          name: 'Some unit',
          id: 1,
          location: 'Some place',
          state: {
            state: ProcessUnitStateEnum.InProgress,
            progress_pct: 30,
            last_seen_date: new Date().toJSON(),
          },
        },
        {
          name: 'Some other unit',
          id: 2,
          location: 'Some place else',
          state: {
            state: ProcessUnitStateEnum.Ready,
            progress_pct: 90,
            last_seen_date: new Date().toJSON(),
          },
        },
        {
          name: 'Some third unit',
          id: 3,
          location: 'Some third place',
          state: {
            state: ProcessUnitStateEnum.NotOnline,
            progress_pct: 90,
            last_seen_date: new Date().toJSON(),
          },
        },
      ]),
    );
  }),
];
