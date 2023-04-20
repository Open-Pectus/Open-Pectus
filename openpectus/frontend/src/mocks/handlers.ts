import { rest } from 'msw';
import { InProgress, NotOnline, ProcessUnit, Ready } from '../app/api';

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
      ]),
    );
  }),
];
