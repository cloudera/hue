var headcount = [
  {date: "1/2009", dept: "eng", type: "perm", headcount: 140},
  {date: "1/2009", dept: "eng", type: "temp", headcount: 39},
  {date: "1/2009", dept: "sales", type: "perm", headcount: 209},
  {date: "1/2009", dept: "sales", type: "temp", headcount: 123},
  {date: "4/2009", dept: "eng", type: "perm", headcount: 160},
  {date: "4/2009", dept: "eng", type: "temp", headcount: 44},
  {date: "4/2009", dept: "sales", type: "perm", headcount: 229},
  {date: "4/2009", dept: "sales", type: "temp", headcount: 113},
  {date: "7/2009", dept: "eng", type: "perm", headcount: 174},
  {date: "7/2009", dept: "eng", type: "temp", headcount: 41},
  {date: "7/2009", dept: "sales", type: "perm", headcount: 224},
  {date: "7/2009", dept: "sales", type: "temp", headcount: 169},
  {date: "10/2009", dept: "eng", type: "perm", headcount: 190},
  {date: "10/2009", dept: "eng", type: "temp", headcount: 43},
  {date: "10/2009", dept: "sales", type: "perm", headcount: 232},
  {date: "10/2009", dept: "sales", type: "temp", headcount: 185}
];

(function() {
  var df = pv.Format.date("%m/%y");
  headcount.forEach(function(d) { d.date = df.parse(d.date); });
})();
