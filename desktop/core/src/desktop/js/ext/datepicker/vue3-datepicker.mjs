import { defineComponent as B, openBlock as D, createElementBlock as S, normalizeClass as I, normalizeStyle as se, withModifiers as C, createElementVNode as c, renderSlot as F, createBlock as N, resolveDynamicComponent as fe, withCtx as M, Fragment as H, createCommentVNode as pe, renderList as Z, toDisplayString as O, computed as u, resolveComponent as q, createTextVNode as K, ref as $, watch as ae, nextTick as ge, watchEffect as X, withDirectives as P, mergeProps as ye, vModelText as ve, vShow as R, createVNode as A } from "vue";
import { isValid as w, startOfDecade as be, endOfDecade as De, eachYearOfInterval as he, getYear as L, getDecade as U, isBefore as j, isAfter as Y, subYears as re, addYears as de, startOfYear as ke, endOfYear as we, format as z, eachMonthOfInterval as Le, isSameMonth as ee, isSameYear as ne, startOfMonth as ue, endOfMonth as me, startOfWeek as $e, endOfWeek as Se, setDay as Ve, eachDayOfInterval as _e, isSameDay as x, isWithinInterval as Oe, startOfDay as qe, endOfDay as Ce, subMonths as Me, addMonths as Pe, set as ie, isSameHour as Fe, isSameMinute as Be, parse as le, max as Te, min as Ee } from "date-fns";
const Re = ["year", "month", "day", "time", "custom"], Ie = B({
  emits: {
    elementClick: (e) => w(e),
    left: () => !0,
    right: () => !0,
    heading: () => !0
  },
  props: {
    headingClickable: {
      type: Boolean,
      default: !1
    },
    leftDisabled: {
      type: Boolean,
      default: !1
    },
    rightDisabled: {
      type: Boolean,
      default: !1
    },
    columnCount: {
      type: Number,
      default: 7
    },
    items: {
      type: Array,
      default: () => []
    },
    viewMode: {
      type: String,
      required: !0,
      validate: (e) => typeof e == "string" && Re.includes(e)
    }
  }
}), T = (e, t) => {
  const r = e.__vccOpts || e;
  for (const [l, o] of t)
    r[l] = o;
  return r;
}, He = { class: "v3dp__heading" }, je = ["disabled"], Ye = /* @__PURE__ */ c("svg", {
  class: "v3dp__heading__icon",
  xmlns: "http://www.w3.org/2000/svg",
  viewBox: "0 0 6 8"
}, [
  /* @__PURE__ */ c("g", {
    fill: "none",
    "fill-rule": "evenodd"
  }, [
    /* @__PURE__ */ c("path", {
      stroke: "none",
      d: "M-9 16V-8h24v24z"
    }),
    /* @__PURE__ */ c("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M5 0L1 4l4 4"
    })
  ])
], -1), Ne = ["disabled"], Ae = /* @__PURE__ */ c("svg", {
  class: "v3dp__heading__icon",
  xmlns: "http://www.w3.org/2000/svg",
  viewBox: "0 0 6 8"
}, [
  /* @__PURE__ */ c("g", {
    fill: "none",
    "fill-rule": "evenodd"
  }, [
    /* @__PURE__ */ c("path", {
      stroke: "none",
      d: "M15-8v24H-9V-8z"
    }),
    /* @__PURE__ */ c("path", {
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
      d: "M1 8l4-4-4-4"
    })
  ])
], -1), Ue = { class: "v3dp__body" }, We = { class: "v3dp__subheading" }, Ze = /* @__PURE__ */ c("hr", { class: "v3dp__divider" }, null, -1), ze = { class: "v3dp__elements" }, Ke = ["disabled", "onClick"];
function Ge(e, t, r, l, o, p) {
  return D(), S("div", {
    class: I(["v3dp__popout", `v3dp__popout-${e.viewMode}`]),
    style: se({ "--popout-column-definition": `repeat(${e.columnCount}, 1fr)` }),
    onMousedown: t[3] || (t[3] = C(() => {
    }, ["prevent"]))
  }, [
    c("div", He, [
      c("button", {
        class: "v3dp__heading__button v3dp__heading__button__left",
        disabled: e.leftDisabled,
        onClick: t[0] || (t[0] = C((n) => e.$emit("left"), ["stop", "prevent"]))
      }, [
        F(e.$slots, "arrow-left", {}, () => [
          Ye
        ])
      ], 8, je),
      (D(), N(fe(e.headingClickable ? "button" : "span"), {
        class: "v3dp__heading__center",
        onClick: t[1] || (t[1] = C((n) => e.$emit("heading"), ["stop", "prevent"]))
      }, {
        default: M(() => [
          F(e.$slots, "heading")
        ]),
        _: 3
      })),
      c("button", {
        class: "v3dp__heading__button v3dp__heading__button__right",
        disabled: e.rightDisabled,
        onClick: t[2] || (t[2] = C((n) => e.$emit("right"), ["stop", "prevent"]))
      }, [
        F(e.$slots, "arrow-right", {}, () => [
          Ae
        ])
      ], 8, Ne)
    ]),
    c("div", Ue, [
      "subheading" in e.$slots ? (D(), S(H, { key: 0 }, [
        c("div", We, [
          F(e.$slots, "subheading")
        ]),
        Ze
      ], 64)) : pe("", !0),
      c("div", ze, [
        F(e.$slots, "body", {}, () => [
          (D(!0), S(H, null, Z(e.items, (n) => (D(), S("button", {
            key: n.key,
            disabled: n.disabled,
            class: I([
              {
                selected: n.selected,
                current: n.current
              },
              `v3dp__element__button__${e.viewMode}`
            ]),
            onClick: C((a) => e.$emit("elementClick", n.value), ["stop", "prevent"])
          }, [
            c("span", null, O(n.display), 1)
          ], 10, Ke))), 128))
        ])
      ])
    ])
  ], 38);
}
const G = /* @__PURE__ */ T(Ie, [["render", Ge]]), Je = B({
  components: {
    PickerPopup: G
  },
  emits: {
    "update:pageDate": (e) => w(e),
    select: (e) => w(e)
  },
  props: {
    selected: {
      type: Date,
      required: !1
    },
    pageDate: {
      type: Date,
      required: !0
    },
    lowerLimit: {
      type: Date,
      required: !1
    },
    upperLimit: {
      type: Date,
      required: !1
    }
  },
  setup(e, { emit: t }) {
    const r = u(() => be(e.pageDate)), l = u(() => De(e.pageDate)), o = (b, v, i) => !v && !i ? !0 : !(v && L(b) < L(v) || i && L(b) > L(i)), p = u(
      () => he({
        start: r.value,
        end: l.value
      }).map(
        (b) => ({
          value: b,
          key: String(L(b)),
          display: L(b),
          selected: !!e.selected && L(b) === L(e.selected),
          disabled: !o(b, e.lowerLimit, e.upperLimit)
        })
      )
    ), n = u(() => {
      const b = L(r.value), v = L(l.value);
      return `${b} - ${v}`;
    }), a = u(
      () => e.lowerLimit && (U(e.lowerLimit) === U(e.pageDate) || j(e.pageDate, e.lowerLimit))
    ), f = u(
      () => e.upperLimit && (U(e.upperLimit) === U(e.pageDate) || Y(e.pageDate, e.upperLimit))
    );
    return {
      years: p,
      heading: n,
      leftDisabled: a,
      rightDisabled: f,
      previousPage: () => t("update:pageDate", re(e.pageDate, 10)),
      nextPage: () => t("update:pageDate", de(e.pageDate, 10))
    };
  }
});
function Qe(e, t, r, l, o, p) {
  const n = q("picker-popup");
  return D(), N(n, {
    columnCount: 3,
    leftDisabled: e.leftDisabled,
    rightDisabled: e.rightDisabled,
    items: e.years,
    viewMode: "year",
    onLeft: e.previousPage,
    onRight: e.nextPage,
    onElementClick: t[0] || (t[0] = (a) => e.$emit("select", a))
  }, {
    heading: M(() => [
      K(O(e.heading), 1)
    ]),
    _: 1
  }, 8, ["leftDisabled", "rightDisabled", "items", "onLeft", "onRight"]);
}
const Xe = /* @__PURE__ */ T(Je, [["render", Qe]]), xe = B({
  components: {
    PickerPopup: G
  },
  emits: {
    "update:pageDate": (e) => w(e),
    select: (e) => w(e),
    back: () => !0
  },
  props: {
    /**
     * Currently selected date, needed for highlighting
     */
    selected: {
      type: Date,
      required: !1
    },
    pageDate: {
      type: Date,
      required: !0
    },
    format: {
      type: String,
      required: !1,
      default: "LLL"
    },
    locale: {
      type: Object,
      required: !1
    },
    lowerLimit: {
      type: Date,
      required: !1
    },
    upperLimit: {
      type: Date,
      required: !1
    }
  },
  setup(e, { emit: t }) {
    const r = u(() => ke(e.pageDate)), l = u(() => we(e.pageDate)), o = u(
      () => (v) => z(v, e.format, {
        locale: e.locale
      })
    ), p = (v, i, h) => !i && !h ? !0 : !(i && j(v, ue(i)) || h && Y(v, me(h))), n = u(
      () => Le({
        start: r.value,
        end: l.value
      }).map(
        (v) => ({
          value: v,
          display: o.value(v),
          key: o.value(v),
          selected: !!e.selected && ee(e.selected, v),
          disabled: !p(v, e.lowerLimit, e.upperLimit)
        })
      )
    ), a = u(() => L(r.value)), f = u(
      () => e.lowerLimit && (ne(e.lowerLimit, e.pageDate) || j(e.pageDate, e.lowerLimit))
    ), V = u(
      () => e.upperLimit && (ne(e.upperLimit, e.pageDate) || Y(e.pageDate, e.upperLimit))
    );
    return {
      months: n,
      heading: a,
      leftDisabled: f,
      rightDisabled: V,
      previousPage: () => t("update:pageDate", re(e.pageDate, 1)),
      nextPage: () => t("update:pageDate", de(e.pageDate, 1))
    };
  }
});
function et(e, t, r, l, o, p) {
  const n = q("picker-popup");
  return D(), N(n, {
    headingClickable: "",
    columnCount: 3,
    items: e.months,
    leftDisabled: e.leftDisabled,
    rightDisabled: e.rightDisabled,
    viewMode: "month",
    onLeft: e.previousPage,
    onRight: e.nextPage,
    onHeading: t[0] || (t[0] = (a) => e.$emit("back")),
    onElementClick: t[1] || (t[1] = (a) => e.$emit("select", a))
  }, {
    heading: M(() => [
      K(O(e.heading), 1)
    ]),
    _: 1
  }, 8, ["items", "leftDisabled", "rightDisabled", "onLeft", "onRight"]);
}
const tt = /* @__PURE__ */ T(xe, [["render", et]]), at = B({
  components: {
    PickerPopup: G
  },
  emits: {
    "update:pageDate": (e) => w(e),
    select: (e) => w(e),
    back: () => !0
  },
  props: {
    selected: {
      type: Date,
      required: !1
    },
    pageDate: {
      type: Date,
      required: !0
    },
    format: {
      type: String,
      required: !1,
      default: "dd"
    },
    headingFormat: {
      type: String,
      required: !1,
      default: "LLLL yyyy"
    },
    weekdayFormat: {
      type: String,
      required: !1,
      default: "EE"
    },
    locale: {
      type: Object,
      required: !1
    },
    weekStartsOn: {
      type: Number,
      required: !1,
      default: 1,
      validator: (e) => typeof e == "number" && Number.isInteger(e) && e >= 0 && e <= 6
    },
    lowerLimit: {
      type: Date,
      required: !1
    },
    upperLimit: {
      type: Date,
      required: !1
    },
    disabledDates: {
      type: Object,
      required: !1
    },
    allowOutsideInterval: {
      type: Boolean,
      required: !1,
      default: !1
    }
  },
  setup(e, { emit: t }) {
    const r = u(
      () => (g) => (y) => z(y, g, {
        locale: e.locale,
        weekStartsOn: e.weekStartsOn
      })
    ), l = u(() => ue(e.pageDate)), o = u(() => me(e.pageDate)), p = u(() => ({
      start: l.value,
      end: o.value
    })), n = u(() => ({
      start: $e(l.value, {
        weekStartsOn: e.weekStartsOn
      }),
      end: Se(o.value, {
        weekStartsOn: e.weekStartsOn
      })
    })), a = u(() => {
      const g = e.weekStartsOn, y = r.value(e.weekdayFormat);
      return Array.from(Array(7)).map((m, k) => (g + k) % 7).map(
        (m) => Ve(/* @__PURE__ */ new Date(), m, {
          weekStartsOn: e.weekStartsOn
        })
      ).map(y);
    }), f = (g, y, m, k) => {
      var E, J;
      return (E = k == null ? void 0 : k.dates) != null && E.some((te) => x(g, te)) || (J = k == null ? void 0 : k.predicate) != null && J.call(k, g) ? !1 : !y && !m ? !0 : !(y && j(g, qe(y)) || m && Y(g, Ce(m)));
    }, V = u(() => {
      const g = /* @__PURE__ */ new Date(), y = r.value(e.format);
      return _e(n.value).map(
        (m) => ({
          value: m,
          display: y(m),
          selected: !!e.selected && x(e.selected, m),
          current: x(g, m),
          disabled: !e.allowOutsideInterval && !Oe(m, p.value) || !f(
            m,
            e.lowerLimit,
            e.upperLimit,
            e.disabledDates
          ),
          key: r.value("yyyy-MM-dd")(m)
        })
      );
    }), d = u(
      () => r.value(e.headingFormat)(e.pageDate)
    ), b = u(
      () => e.lowerLimit && (ee(e.lowerLimit, e.pageDate) || j(e.pageDate, e.lowerLimit))
    ), v = u(
      () => e.upperLimit && (ee(e.upperLimit, e.pageDate) || Y(e.pageDate, e.upperLimit))
    );
    return {
      weekDays: a,
      days: V,
      heading: d,
      leftDisabled: b,
      rightDisabled: v,
      previousPage: () => t("update:pageDate", Me(e.pageDate, 1)),
      nextPage: () => t("update:pageDate", Pe(e.pageDate, 1))
    };
  }
});
function nt(e, t, r, l, o, p) {
  const n = q("picker-popup");
  return D(), N(n, {
    headingClickable: "",
    leftDisabled: e.leftDisabled,
    rightDisabled: e.rightDisabled,
    items: e.days,
    viewMode: "day",
    onLeft: e.previousPage,
    onRight: e.nextPage,
    onHeading: t[0] || (t[0] = (a) => e.$emit("back")),
    onElementClick: t[1] || (t[1] = (a) => e.$emit("select", a))
  }, {
    heading: M(() => [
      K(O(e.heading), 1)
    ]),
    subheading: M(() => [
      (D(!0), S(H, null, Z(e.weekDays, (a, f) => (D(), S("span", {
        key: a,
        class: I(`v3dp__subheading__weekday__${f}`)
      }, O(a), 3))), 128))
    ]),
    _: 1
  }, 8, ["leftDisabled", "rightDisabled", "items", "onLeft", "onRight"]);
}
const it = /* @__PURE__ */ T(at, [["render", nt]]);
function oe(e, t) {
  const r = e.getBoundingClientRect(), l = {
    height: e.clientHeight,
    width: e.clientWidth
  }, o = t.getBoundingClientRect();
  if (!(o.top >= r.top && o.bottom <= r.top + l.height)) {
    const n = o.top - r.top, a = o.bottom - r.bottom;
    Math.abs(n) < Math.abs(a) ? e.scrollTop += n : e.scrollTop += a;
  }
}
const lt = B({
  components: {
    PickerPopup: G
  },
  emits: {
    select: (e) => w(e),
    back: () => !0
  },
  props: {
    selected: {
      type: Date,
      required: !1
    },
    pageDate: {
      type: Date,
      required: !0
    },
    visible: {
      type: Boolean,
      required: !0
    },
    disabledTime: {
      type: Object,
      required: !1
    }
  },
  setup(e, { emit: t }) {
    const r = $(null), l = $(null), o = u(() => e.pageDate ?? e.selected), p = $(o.value.getHours()), n = $(o.value.getMinutes());
    ae(
      () => e.selected,
      (i) => {
        let h = 0, g = 0;
        i && (h = i.getHours(), g = i.getMinutes()), p.value = h, n.value = g;
      }
    );
    const a = u(
      () => [...Array(24).keys()].map(
        (i) => ({
          value: i,
          date: ie(new Date(o.value.getTime()), {
            hours: i,
            minutes: n.value,
            seconds: 0
          }),
          selected: p.value === i,
          ref: $(null)
        })
      )
    ), f = u(
      () => [...Array(60).keys()].map((i) => ({
        value: i,
        date: ie(new Date(o.value.getTime()), {
          hours: p.value,
          minutes: i,
          seconds: 0
        }),
        selected: n.value === i,
        ref: $(null)
      }))
    ), V = (i) => {
      n.value = i.value, t("select", i.date);
    }, d = () => {
      const i = a.value.find(
        (g) => {
          var y, m;
          return ((m = (y = g.ref.value) == null ? void 0 : y.classList) == null ? void 0 : m.contains("selected")) ?? !1;
        }
      ), h = f.value.find(
        (g) => {
          var y, m;
          return ((m = (y = g.ref.value) == null ? void 0 : y.classList) == null ? void 0 : m.contains("selected")) ?? !1;
        }
      );
      i && h && (oe(r.value, i.ref.value), oe(l.value, h.ref.value));
    };
    return ae(
      () => e.visible,
      (i) => {
        i && ge(d);
      }
    ), {
      hoursListRef: r,
      minutesListRef: l,
      hours: p,
      minutes: n,
      hoursList: a,
      minutesList: f,
      padStartZero: (i) => `0${i}`.substr(-2),
      selectMinutes: V,
      isEnabled: (i) => {
        var h, g, y, m;
        return !((g = (h = e.disabledTime) == null ? void 0 : h.dates) != null && g.some(
          (k) => Fe(i, k) && Be(i, k)
        ) || (m = (y = e.disabledTime) == null ? void 0 : y.predicate) != null && m.call(y, i));
      },
      scroll: d
    };
  }
});
const ot = {
  ref: "hoursListRef",
  class: "v3dp__column"
}, st = ["disabled", "onClick"], rt = {
  ref: "minutesListRef",
  class: "v3dp__column"
}, dt = ["disabled", "onClick"];
function ut(e, t, r, l, o, p) {
  const n = q("picker-popup");
  return D(), N(n, {
    headingClickable: "",
    columnCount: 2,
    leftDisabled: !0,
    rightDisabled: !0,
    viewMode: "time",
    onHeading: t[0] || (t[0] = (a) => e.$emit("back"))
  }, {
    heading: M(() => [
      K(O(e.padStartZero(e.hours)) + ":" + O(e.padStartZero(e.minutes)), 1)
    ]),
    body: M(() => [
      c("div", ot, [
        (D(!0), S(H, null, Z(e.hoursList, (a) => (D(), S("button", {
          key: a.value,
          ref_for: !0,
          ref: a.ref,
          class: I([{ selected: a.selected }, "v3dp__element_button__hour"]),
          disabled: !e.isEnabled(a.date),
          onClick: C((f) => e.hours = a.value, ["stop", "prevent"])
        }, [
          c("span", null, O(e.padStartZero(a.value)), 1)
        ], 10, st))), 128))
      ], 512),
      c("div", rt, [
        (D(!0), S(H, null, Z(e.minutesList, (a) => (D(), S("button", {
          key: a.value,
          ref_for: !0,
          ref: a.ref,
          class: I([{ selected: a.selected }, "v3dp__element_button__minute"]),
          disabled: !e.isEnabled(a.date),
          onClick: C((f) => e.selectMinutes(a), ["stop", "prevent"])
        }, [
          c("span", null, O(e.padStartZero(a.value)), 1)
        ], 10, dt))), 128))
      ], 512)
    ]),
    _: 1
  });
}
const mt = /* @__PURE__ */ T(lt, [["render", ut], ["__scopeId", "data-v-81ac698d"]]), W = ["time", "day", "month", "year"], ct = (e, t, r = void 0) => {
  let l = r || /* @__PURE__ */ new Date();
  return e && (l = Te([e, l])), t && (l = Ee([t, l])), l;
}, ft = B({
  components: {
    YearPicker: Xe,
    MonthPicker: tt,
    DayPicker: it,
    TimePicker: mt
  },
  inheritAttrs: !1,
  props: {
    placeholder: {
      type: String,
      default: ""
    },
    /**
     * `v-model` for selected date
     */
    modelValue: {
      type: Date,
      required: !1
    },
    /**
     * Dates not available for picking
     */
    disabledDates: {
      type: Object,
      required: !1
    },
    allowOutsideInterval: {
      type: Boolean,
      required: !1,
      default: !1
    },
    /**
     * Time not available for picking
     */
    disabledTime: {
      type: Object,
      required: !1
    },
    /**
     * Upper limit for available dates for picking
     */
    upperLimit: {
      type: Date,
      required: !1
    },
    /**
     * Lower limit for available dates for picking
     */
    lowerLimit: {
      type: Date,
      required: !1
    },
    /**
     * View on which the date picker should open. Can be either `year`, `month`, `day` or `time`
     */
    startingView: {
      type: String,
      required: !1,
      default: "day",
      validate: (e) => typeof e == "string" && W.includes(e)
    },
    /**
     * Date which should be the "center" of the initial view.
     * When an empty datepicker opens, it focuses on the month/year
     * that contains this date
     */
    startingViewDate: {
      type: Date,
      required: !1,
      default: () => /* @__PURE__ */ new Date()
    },
    /**
     * `date-fns`-type formatting for a month view heading
     */
    dayPickerHeadingFormat: {
      type: String,
      required: !1,
      default: "LLLL yyyy"
    },
    /**
     * `date-fns`-type formatting for the month picker view
     */
    monthListFormat: {
      type: String,
      required: !1,
      default: "LLL"
    },
    /**
     * `date-fns`-type formatting for a line of weekdays on day view
     */
    weekdayFormat: {
      type: String,
      required: !1,
      default: "EE"
    },
    /**
     * `date-fns`-type formatting for the day picker view
     */
    dayFormat: {
      type: String,
      required: !1,
      default: "dd"
    },
    /**
     * `date-fns`-type format in which the string in the input should be both
     * parsed and displayed
     */
    inputFormat: {
      type: String,
      required: !1,
      default: "yyyy-MM-dd"
    },
    /**
     * [`date-fns` locale object](https://date-fns.org/v2.16.1/docs/I18n#usage).
     * Used in string formatting (see default `dayPickerHeadingFormat`)
     */
    locale: {
      type: Object,
      required: !1
    },
    /**
     * Day on which the week should start.
     *
     * Number from 0 to 6, where 0 is Sunday and 6 is Saturday.
     * Week starts with a Monday (1) by default
     */
    weekStartsOn: {
      type: Number,
      required: !1,
      default: 1,
      validator: (e) => [0, 1, 2, 3, 4, 5, 6].includes(e)
    },
    /**
     * Disables datepicker and prevents it's opening
     */
    disabled: {
      type: Boolean,
      required: !1,
      default: !1
    },
    /**
     * Clears selected date
     */
    clearable: {
      type: Boolean,
      required: !1,
      default: !1
    },
    /*
     * Allows user to input date manually
     */
    typeable: {
      type: Boolean,
      required: !1,
      default: !1
    },
    /**
     * If set, lower-level views won't show
     */
    minimumView: {
      type: String,
      required: !1,
      default: "day",
      validate: (e) => typeof e == "string" && W.includes(e)
    }
  },
  emits: {
    "update:modelValue": (e) => e == null || w(e),
    decadePageChanged: (e) => !0,
    yearPageChanged: (e) => !0,
    monthPageChanged: (e) => !0,
    opened: () => !0,
    closed: () => !0
  },
  setup(e, { emit: t, attrs: r }) {
    const l = $("none"), o = $(e.startingViewDate), p = $(null), n = $(!1), a = $("");
    X(() => {
      const s = le(a.value, e.inputFormat, /* @__PURE__ */ new Date(), {
        locale: e.locale
      });
      w(s) && (o.value = s);
    }), X(
      () => a.value = e.modelValue && w(e.modelValue) ? z(e.modelValue, e.inputFormat, {
        locale: e.locale
      }) : ""
    );
    const f = (s = "none") => {
      e.disabled || (s !== "none" && l.value === "none" && (o.value = e.modelValue || ct(e.lowerLimit, e.upperLimit, o.value)), l.value = s, t(s !== "none" ? "opened" : "closed"));
    };
    X(() => {
      e.disabled && (l.value = "none");
    });
    const V = (s, _) => {
      o.value = _, s === "year" ? t("decadePageChanged", _) : s === "month" ? t("yearPageChanged", _) : s === "day" && t("monthPageChanged", _);
    }, d = (s) => {
      o.value = s, e.minimumView === "year" ? (f("none"), t("update:modelValue", s)) : l.value = "month";
    }, b = (s) => {
      o.value = s, e.minimumView === "month" ? (f("none"), t("update:modelValue", s)) : l.value = "day";
    }, v = (s) => {
      o.value = s, e.minimumView === "day" ? (f("none"), t("update:modelValue", s)) : l.value = "time";
    }, i = (s) => {
      f("none"), t("update:modelValue", s);
    }, h = () => {
      e.clearable && (f("none"), t("update:modelValue", null), o.value = e.startingViewDate);
    }, g = () => n.value = !0, y = () => f(E.value), m = () => {
      n.value = !1, f();
    }, k = (s) => {
      const _ = s.keyCode ? s.keyCode : s.which;
      if ([
        27,
        // escape
        13
        // enter
      ].includes(_) && p.value.blur(), e.typeable) {
        const Q = le(
          p.value.value,
          e.inputFormat,
          /* @__PURE__ */ new Date(),
          { locale: e.locale }
        );
        w(Q) && a.value === z(Q, e.inputFormat, { locale: e.locale }) && (a.value = p.value.value, t("update:modelValue", Q));
      }
    }, E = u(() => {
      const s = W.indexOf(e.startingView), _ = W.indexOf(e.minimumView);
      return s < _ ? e.minimumView : e.startingView;
    });
    return {
      blur: m,
      focus: y,
      click: g,
      input: a,
      inputRef: p,
      pageDate: o,
      renderView: f,
      updatePageDate: V,
      selectYear: d,
      selectMonth: b,
      selectDay: v,
      selectTime: i,
      keyUp: k,
      viewShown: l,
      goBackFromTimepicker: () => e.startingView === "time" && e.minimumView === "time" ? null : l.value = "day",
      clearModelValue: h,
      initialView: E,
      log: (s) => console.log(s),
      variables: (s) => Object.fromEntries(
        Object.entries(s ?? {}).filter(([_, ce]) => _.startsWith("--"))
      )
    };
  }
});
const pt = { class: "v3dp__input_wrapper" }, gt = ["readonly", "placeholder", "disabled", "tabindex"], yt = { class: "v3dp__clearable" };
function vt(e, t, r, l, o, p) {
  const n = q("year-picker"), a = q("month-picker"), f = q("day-picker"), V = q("time-picker");
  return D(), S("div", {
    class: "v3dp__datepicker",
    style: se(e.variables(e.$attrs.style))
  }, [
    c("div", pt, [
      P(c("input", ye({
        type: "text",
        ref: "inputRef",
        readonly: !e.typeable,
        "onUpdate:modelValue": t[0] || (t[0] = (d) => e.input = d)
      }, e.$attrs, {
        placeholder: e.placeholder,
        disabled: e.disabled,
        tabindex: e.disabled ? -1 : 0,
        onKeyup: t[1] || (t[1] = (...d) => e.keyUp && e.keyUp(...d)),
        onBlur: t[2] || (t[2] = (...d) => e.blur && e.blur(...d)),
        onFocus: t[3] || (t[3] = (...d) => e.focus && e.focus(...d)),
        onClick: t[4] || (t[4] = (...d) => e.click && e.click(...d))
      }), null, 16, gt), [
        [ve, e.input]
      ]),
      P(c("div", yt, [
        F(e.$slots, "clear", { onClear: e.clearModelValue }, () => [
          c("i", {
            onClick: t[5] || (t[5] = (d) => e.clearModelValue())
          }, "x")
        ])
      ], 512), [
        [R, e.clearable && e.modelValue]
      ])
    ]),
    P(A(n, {
      pageDate: e.pageDate,
      "onUpdate:pageDate": t[6] || (t[6] = (d) => e.updatePageDate("year", d)),
      selected: e.modelValue,
      lowerLimit: e.lowerLimit,
      upperLimit: e.upperLimit,
      onSelect: e.selectYear
    }, null, 8, ["pageDate", "selected", "lowerLimit", "upperLimit", "onSelect"]), [
      [R, e.viewShown === "year"]
    ]),
    P(A(a, {
      pageDate: e.pageDate,
      "onUpdate:pageDate": t[7] || (t[7] = (d) => e.updatePageDate("month", d)),
      selected: e.modelValue,
      onSelect: e.selectMonth,
      lowerLimit: e.lowerLimit,
      upperLimit: e.upperLimit,
      format: e.monthListFormat,
      locale: e.locale,
      onBack: t[8] || (t[8] = (d) => e.viewShown = "year")
    }, null, 8, ["pageDate", "selected", "onSelect", "lowerLimit", "upperLimit", "format", "locale"]), [
      [R, e.viewShown === "month"]
    ]),
    P(A(f, {
      pageDate: e.pageDate,
      "onUpdate:pageDate": t[9] || (t[9] = (d) => e.updatePageDate("day", d)),
      selected: e.modelValue,
      weekStartsOn: e.weekStartsOn,
      lowerLimit: e.lowerLimit,
      upperLimit: e.upperLimit,
      headingFormat: e.dayPickerHeadingFormat,
      disabledDates: e.disabledDates,
      locale: e.locale,
      weekdayFormat: e.weekdayFormat,
      "allow-outside-interval": e.allowOutsideInterval,
      format: e.dayFormat,
      onSelect: e.selectDay,
      onBack: t[10] || (t[10] = (d) => e.viewShown = "month")
    }, null, 8, ["pageDate", "selected", "weekStartsOn", "lowerLimit", "upperLimit", "headingFormat", "disabledDates", "locale", "weekdayFormat", "allow-outside-interval", "format", "onSelect"]), [
      [R, e.viewShown === "day"]
    ]),
    P(A(V, {
      pageDate: e.pageDate,
      visible: e.viewShown === "time",
      selected: e.modelValue,
      disabledTime: e.disabledTime,
      onSelect: e.selectTime,
      onBack: e.goBackFromTimepicker
    }, null, 8, ["pageDate", "visible", "selected", "disabledTime", "onSelect", "onBack"]), [
      [R, e.viewShown === "time"]
    ])
  ], 4);
}
const ht = /* @__PURE__ */ T(ft, [["render", vt]]);
export {
  ht as default
};
