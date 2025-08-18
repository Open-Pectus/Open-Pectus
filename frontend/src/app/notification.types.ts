import { NotificationScope, NotificationTopic } from './api';

export const notificationScopes: Record<NotificationScope, NotificationScope> = {
  process_units_i_have_access_to: 'process_units_i_have_access_to',
  process_units_with_runs_ive_contributed_to: 'process_units_with_runs_ive_contributed_to',
  specific_process_units: 'specific_process_units',
};

export const topics: Record<NotificationTopic, NotificationTopic> = {
  block_start: 'block_start',
  method_error: 'method_error',
  network_errors: 'network_errors',
  new_contributor: 'new_contributor',
  notification_cmd: 'notification_cmd',
  run_pause: 'run_pause',
  run_start: 'run_start',
  run_stop: 'run_stop',
  watch_triggered: 'watch_triggered',
};
