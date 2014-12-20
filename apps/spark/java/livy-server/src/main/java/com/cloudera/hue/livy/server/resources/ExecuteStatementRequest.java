package com.cloudera.hue.livy.server.resources;

import org.hibernate.validator.constraints.NotEmpty;

/**
 * Created by erickt on 11/25/14.
 */
public class ExecuteStatementRequest {
    @NotEmpty
    private String statement;

    public String getStatement() {
        return statement;
    }
}
