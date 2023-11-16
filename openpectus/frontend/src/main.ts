import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { setupWorker } from 'msw/browser';
import { AppModule } from './app/app.module';
import { handlers } from './msw/handlers';
import { MswEnablement } from './msw/msw-enablement';

if(MswEnablement.isEnabled) {
  const worker = setupWorker(...handlers);
  await worker.start({
    onUnhandledRequest: (request: Request) => {
      const url = new URL(request.url);
      const pathname = url.pathname;
      if(pathname.startsWith('/assets')
         || pathname.startsWith('/node_modules')
         || pathname.startsWith('/src')
         || pathname.startsWith('/api/trigger-pubsub')
         || pathname.endsWith('.ico')
         || pathname.endsWith('.js')
         || pathname.endsWith('.json')
         || pathname.endsWith('.ttf')
         || pathname.endsWith('.wasm')
         || url.host !== window.location.host
      ) {
        return;
      }
      console.warn(`url ${request.url} was not mocked by MSW`);
    },
  });
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
