import React, { useEffect, useState } from 'react';
import Alert from 'cuix/dist/components/Alert/Alert';

import huePubSub from 'utils/huePubSub';
import './AlertComponent.scss';

// Define the type for your error object
interface ErrorAlert {
    message: string;
}

const AlertComponent: React.FC = () => {
    const [errors, setErrors] = useState<ErrorAlert[]>([]);

    useEffect(() => {
        const hueSub = huePubSub.subscribe('hue.global.error', (errorObj: ErrorAlert) => {
            setErrors((prevData) => [...prevData, errorObj]);
        });
        return () => {
            hueSub.remove();
        };
    }, []);

    const handleClose = (errorObj: ErrorAlert, id: number) => {
        const filteredErrors = errors.filter((_, index) => index !== id);
        setErrors(filteredErrors);
    };

    return (
        <div className='flash-messages cuix antd'>
            {errors.map((errorObj, index) => (
                <Alert
                    key={index}
                    type="error"
                    message={errorObj.message}
                    closable={true}
                    onClose={() => handleClose(errorObj, index)}
                />
            ))}
        </div>
    );
};

export default AlertComponent;