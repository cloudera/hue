// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Spliterator;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import lombok.EqualsAndHashCode;
import lombok.ToString;
import lombok.Value;

/**
 * Value object holding the Sort information
 */
@Value
public class SortRequest implements Iterable<SortRequest.Order> {
  public static Direction DEFAULT_DIRECTION = Direction.DESC;

  private List<Order> orders;

  public SortRequest(List<Order> orders) {
    this.orders = orders;
  }

  public SortRequest(Direction direction, String... properties) {
    this(Arrays.asList(properties).stream().map(x -> new Order(x, direction)).collect(Collectors.toList()));
  }

  public SortRequest(Order... orders) {
    this(Arrays.asList(orders));
  }

  public SortRequest(String... properties) {
    this(DEFAULT_DIRECTION, properties);
  }

  public SortRequest and(SortRequest request) {
    List<SortRequest.Order> newOrders = new ArrayList<>();
    this.orders.forEach((x) -> newOrders.add(new Order(x.getProperty(), x.getDirection())));
    request.orders.forEach((x) -> newOrders.add(new Order(x.getProperty(), x.getDirection())));
    return new SortRequest(newOrders);
  }

  @Override
  public Iterator<Order> iterator() {
    return orders.iterator();
  }

  @Override
  public void forEach(Consumer<? super Order> action) {
    orders.forEach(action);
  }

  @Override
  public Spliterator<Order> spliterator() {
    return orders.spliterator();
  }


  /**
   * Value object holding the ordering information for a property.
   */
  @ToString
  @EqualsAndHashCode
  public static class Order {
    private final String property;
    private final Direction direction;

    public Order(String property) {
      this(property, SortRequest.DEFAULT_DIRECTION);
    }

    public Order(String property, Direction direction) {
      this.property = property;
      this.direction = direction;
    }


    public String getProperty() {
      return property;
    }

    public Direction getDirection() {
      return direction;
    }

    public boolean isAscending() {
      return getDirection().isAscending();
    }

    public boolean isDescending() {
      return getDirection().isDescending();
    }

    public Order with(Direction direction) {
      return new Order(getProperty(), direction);
    }

    public Order with(String property) {
      return new Order(property, getDirection());
    }


  }

  /**
   * Enum to define the ordering direction
   */
  public enum Direction {
    ASC,
    DESC;

    public Direction fromString(String direction) {
      if (direction == null) {
        return SortRequest.DEFAULT_DIRECTION;
      }
      return valueOf(direction.toUpperCase());
    }

    public boolean isAscending() {
      return this == Direction.ASC;
    }

    public boolean isDescending() {
      return this == Direction.DESC;
    }
  }
}
