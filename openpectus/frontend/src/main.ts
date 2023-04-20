import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { worker } from './mocks/browser';


if(process.env['NODE_ENV'] === 'development') {
  const {worker} = require('./mocks/browser');
  worker.start().then();
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
