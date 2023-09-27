import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { MockedRequest, setupWorker } from 'msw';
import { AppModule } from './app/app.module';
import { handlers } from './msw/handlers';
import { MswEnablement } from './msw/msw-enablement';

if(MswEnablement.isEnabled) {
  const worker = setupWorker(...handlers);
  await worker.start({
    onUnhandledRequest: (request: MockedRequest) => {
      const pathname = request.url.pathname;
      if(pathname.startsWith('/assets')
         || pathname.startsWith('/node_modules')
         || pathname.startsWith('/src')
         || pathname.endsWith('.ico')
         || pathname.endsWith('.js')
         || pathname.endsWith('.json')
         || pathname.endsWith('.ttf')
         || pathname.endsWith('.wasm')
         || request.url.host !== window.location.host
      ) {
        return;
      }
      console.warn(`url ${request.url} was not mocked by MSW`);
    },
  });
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
