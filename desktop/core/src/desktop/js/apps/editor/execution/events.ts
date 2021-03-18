import { Session } from 'apps/editor/execution/api';
import ExecutionResult from './executionResult';
import Executable, { ExecutionStatus } from './executable';
import ExecutionLogs from './executionLogs';

export const EXECUTABLE_TRANSITIONED_TOPIC = 'hue.executable.status.transitioned';
export interface ExecutableTransitionedEvent {
  newStatus: ExecutionStatus;
  oldStatus: ExecutionStatus;
  executable: Executable;
}

export const EXECUTABLE_UPDATED_TOPIC = 'hue.executable.updated';
export type ExecutableUpdatedEvent = Executable;

export const EXECUTABLE_LOGS_UPDATED_TOPIC = 'hue.executable.logs.updated';
export type ExecutableLogsUpdatedEvent = ExecutionLogs;

export const EXECUTABLE_RESULT_UPDATED_TOPIC = 'hue.executable.result.updated';
export type ExecutableResultUpdatedEvent = ExecutionResult;

export const SHOW_SESSION_AUTH_MODAL_TOPIC = 'show.session.auth.modal';
export interface ShowSessionAuthModalEvent {
  message?: string;
  session: Session;
  resolve(): void;
  reject(): void;
}
