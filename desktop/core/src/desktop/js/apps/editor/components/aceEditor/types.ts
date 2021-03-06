import { StatementDetails } from '../../../../parse/types';

export interface ActiveStatementChangedEvent extends Event {
  detail: ActiveStatementChangedEventDetails;
}

export interface ActiveStatementChangedEventDetails extends StatementDetails {
  id: string;
  editorChangeTime: number;
  activeStatementIndex: number;
  totalStatementCount: number;
}
