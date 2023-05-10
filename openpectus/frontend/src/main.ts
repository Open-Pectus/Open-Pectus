import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { MockedRequest } from 'msw';
import { AppModule } from './app/app.module';
import { worker } from './msw/browser';


if(process.env['NODE_ENV'] === 'development') {
  const {worker} = require('./msw/browser');
  worker.start({
    onUnhandledRequest: (request: MockedRequest) => {
      const pathname = request.url.pathname;
      if(pathname.startsWith('/assets') ||
         pathname.startsWith('/node_modules') ||
         pathname.startsWith('/src') ||
         pathname === '/codicon.ttf' ||
         pathname === '/favicon.ico'
      ) {
        return;
      }
      console.warn(`url ${request.url} was not mocked by MSW`);
    },
  }).then();
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
