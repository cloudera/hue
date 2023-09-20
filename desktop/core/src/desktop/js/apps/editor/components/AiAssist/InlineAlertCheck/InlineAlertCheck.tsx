import React from 'react';
import { Checkbox } from 'antd';
import { CheckboxChangeEvent } from 'antd/lib/checkbox';
import Alert from 'cuix/dist/components/Alert/Alert';

import './InlineAlertCheck.scss';

export interface InlineAlertCheckProps {
  show: boolean;
  onCheckboxChange: (checked: boolean) => void;
  msg: string | undefined;
  checkboxLabel: string;
}

const InlineAlertCheck = ({
  show,
  onCheckboxChange,
  msg,
  checkboxLabel
}: InlineAlertCheckProps) => {
  return show ? (
    <div className="hue-inline-alert-check">
      <Alert
        description={
          <>
            <p>{msg}</p>
            <Checkbox
              onChange={(e: CheckboxChangeEvent) => {
                onCheckboxChange(e.target.checked);
              }}
            >
              {checkboxLabel}
            </Checkbox>
          </>
        }
        type="warning"
      />
    </div>
  ) : null;
};

export default InlineAlertCheck;
