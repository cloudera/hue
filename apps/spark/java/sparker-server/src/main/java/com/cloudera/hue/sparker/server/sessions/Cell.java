package com.cloudera.hue.sparker.server.sessions;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List;

public class Cell {

    public enum State {
        NOT_READY,
        READY,
        INCOMPLETE,
        RUNNING,
        COMPLETE,
    }

    State state;
    final List<String> input = new ArrayList<String>();
    final List<String> output = new ArrayList<String>();

    final List<String> error = new ArrayList<String>();

    public Cell() {
        this.state = State.NOT_READY;
    }

    @JsonProperty("type")
    public State getState() {
        return state;
    }

    public void setState(State state) {
        this.state = state;
    }

    @JsonProperty("input")
    public List<String> getInput() {
        return input;
    }

    public void addInput(String input) {
        this.input.add(input);
    }

    @JsonProperty("output")
    public List<String> getOutput() {
        return output;
    }

    public void addOutput(String output) {
        this.output.add(output);
    }

    @JsonProperty("error")
    public List<String> getError() {
        return error;
    }

    public void addError(String error) {
        this.error.add(error);
    }
}
