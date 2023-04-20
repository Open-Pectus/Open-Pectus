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
          runtime_msec: 59999,
          state: {
            state: ProcessUnitStateEnum.InProgress,
            progress_pct: 30,
            last_seen_date: new Date().toJSON(),
          },
        },
        {
          name: 'Some other unit with a long title',
          id: 2,
          location: 'Some place else',
          runtime_msec: 456498,
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
          runtime_msec: 12365,
          state: {
            state: ProcessUnitStateEnum.NotOnline,
            progress_pct: 90,
            last_seen_date: new Date().toJSON(),
          },
        },
        {
          name: 'A fourth for linebreak',
          id: 4,
          location: 'Narnia',
          runtime_msec: 85264,
          state: {
            state: ProcessUnitStateEnum.NotOnline,
            progress_pct: 0,
            last_seen_date: new Date().toJSON(),
          },
        },
      ]),
    );
  }),
];
