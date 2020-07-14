// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.pipeline;

import java.util.AbstractCollection;
import java.util.AbstractSet;
import java.util.Collection;
import java.util.Collections;
import java.util.Iterator;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;

/**
 * An unmodifiable view over a map with an adapter function to change value from V1 to V2.
 *
 * @param <K> The key type.
 * @param <V1> The input map value type.
 * @param <V2> The view map value type.
 */
public class ImmutableMapView<K, V1, V2> implements Map<K, V2> {
  private final Map<K, V1> delegate;
  private final Function<V1, V2> mapFn;

  public ImmutableMapView(Map<K, V1> delegate, Function<V1, V2> mapFn) {
    this.delegate = delegate;
    this.mapFn = mapFn;
  }

  private V2 convert(V1 val) {
    return val == null ? null : mapFn.apply(val);
  }

  @Override
  public int size() {
    return delegate.size();
  }

  @Override
  public boolean isEmpty() {
    return delegate.isEmpty();
  }

  @Override
  public boolean containsKey(Object key) {
    return delegate.containsKey(key);
  }

  @Override
  public boolean containsValue(Object value) {
    for (V1 val : delegate.values()) {
      if (Objects.equals(convert(val), value)) {
        return true;
      }
    }
    return false;
  }

  @Override
  public V2 get(Object key) {
    return convert(delegate.get(key));
  }

  @Override
  public V2 put(K key, V2 value) {
    throw new UnsupportedOperationException();
  }

  @Override
  public V2 remove(Object key) {
    throw new UnsupportedOperationException();
  }

  @Override
  public void putAll(Map<? extends K, ? extends V2> m) {
    throw new UnsupportedOperationException();
  }

  @Override
  public void clear() {
    throw new UnsupportedOperationException();
  }

  @Override
  public Set<K> keySet() {
    return Collections.unmodifiableSet(delegate.keySet());
  }

  @Override
  public Collection<V2> values() {
    final Collection<V1> vals = delegate.values();
    return new AbstractCollection<V2>() {
      @Override
      public Iterator<V2> iterator() {
        Iterator<V1> iter = vals.iterator();
        return new Iterator<V2>() {
          @Override
          public boolean hasNext() {
            return iter.hasNext();
          }
          @Override
          public V2 next() {
            return convert(iter.next());
          }
        };
      }

      @Override
      public int size() {
        return vals.size();
      }
    };
  }

  @Override
  public Set<Entry<K, V2>> entrySet() {
    Set<Entry<K, V1>> entries = delegate.entrySet();
    return new AbstractSet<Entry<K, V2>>() {

      @Override
      public Iterator<Entry<K, V2>> iterator() {
        Iterator<Entry<K, V1>> iter = entries.iterator();
        return new Iterator<Entry<K,V2>>() {

          @Override
          public boolean hasNext() {
            return iter.hasNext();
          }

          @Override
          public Entry<K, V2> next() {
            Entry<K, V1> entry = iter.next();
            return new Entry<K, V2>() {
              @Override
              public K getKey() {
                return entry.getKey();
              }

              @Override
              public V2 getValue() {
                return convert(entry.getValue());
              }

              @Override
              public V2 setValue(V2 value) {
                throw new UnsupportedOperationException();
              }
            };
          }
        };
      }

      @Override
      public int size() {
        return entries.size();
      }
    };
  }
}
