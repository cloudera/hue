/*
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */
export default function tableJoins(model, selectedDbName) {
    var entities = model.entities || {};
    //var entities = model.entities || {};
    var joinsByDate = model.results || [];
    var selectedDBName = selectedDbName;

    if(joinsByDate.length < 1){
      return [];
    }

    var joinsArray = [];
    joinsByDate.forEach((item) =>{
      joinsArray.push(item.joins);
    });

    var flatJoins = joinsArray.reduce(
      function(a, b) {
        return a.concat(b);
      },
      []
    );
    var getTable = function(tableId, tables){
        return tables.find( table => table.id == tableId);
    }

    var allJoins = flatJoins.map((item)=>{
      let leftTable = getTable(item.leftTableId, entities.tables);
      let rightTable = getTable(item.rightTableId, entities.tables);
  
      let {id, fullOuterJoinCount, innerJoinCount, leftOuterJoinCount, leftSemiJoinCount, rightOuterJoinCount, totalJoinCount, uniqueJoinCount, unknownJoinCount, algorithm} = item;
      let mappedItem = {
        id, fullOuterJoinCount, innerJoinCount, leftOuterJoinCount, leftSemiJoinCount, rightOuterJoinCount, totalJoinCount, uniqueJoinCount, unknownJoinCount, algorithm,
        fromColumn : leftTable.databaseName +'.' + item.leftTableName + '.' + item.leftColumnName,
        toColumn : rightTable.databaseName +'.' + item.rightTableName + '.' + item.rightColumnName
      }
      return mappedItem;
    });

    /* TEST CODE. Please don't remove. */
    /*
    var allJoins = [{
      id: 1,
      fromColumn: "d1.t1.col1",
      toColumn: "d1.t2.col3",
      totalJoinCount: 1,
      algorithm: 'A'
    },
    {
      id: 2,
      fromColumn: "d1.t1.col1",
      toColumn: "d1.t2.col3",
      totalJoinCount: 1,
      algorithm: 'A'
    },
    {
      id: 3,
      fromColumn: "d1.t1.col1",
      toColumn: "d1.t2.col4",
      totalJoinCount: 1,
      algorithm: 'B'
    },
    {
      id: 4,
      fromColumn: "d1.t1.col1",
      toColumn: "d1.t2.col4",
      totalJoinCount: 1,
      algorithm: 'B'
    },
    {
      id: 5,
      fromColumn: "d1.t1.col1",
      toColumn: "d1.t2.col4",
      totalJoinCount: 1,
      algorithm: 'C'
    },
    {
      id: 6,
      fromColumn: "d1.t2.col3",
      toColumn: "d1.t1.col1",
      totalJoinCount: 1,
      algorithm: 'D'
    },
    {
      id: 7,
      fromColumn: "d1.t2.col4",
      toColumn: "d1.t1.col2",
      totalJoinCount: 1,
      algorithm: 'E'
    }];
    
    */


   var allJoinsByFromColumn =  allJoins.groupBy('fromColumn');

    var allJoinsByToColumn =  allJoins.groupBy('toColumn');

    var finalJoinList = [];

    for (var key in allJoinsByFromColumn) {
        if (!allJoinsByFromColumn.hasOwnProperty(key)) continue;

        var obj = allJoinsByFromColumn[key];
        let localObj = { name: key, imports: [], importsHash: [] };

        let hashCode = {};
        for (var prop in obj) {
            if(!obj.hasOwnProperty(prop)) continue;
            if(!hashCode[obj[prop].toColumn]) {
              hashCode[obj[prop].toColumn] = obj[prop].totalJoinCount;
              localObj.imports.push(obj[prop].toColumn);
              localObj.importsHash.push({hashKey: obj[prop].toColumn, value: hashCode[obj[prop].toColumn]});
            } else {
              hashCode[obj[prop].toColumn] = hashCode[obj[prop].toColumn] + obj[prop].totalJoinCount;
              localObj.importsHash.filterBy('hashKey', obj[prop].toColumn)[0].value = hashCode[obj[prop].toColumn];
            }
        }
        finalJoinList.push(localObj);
    }

    var allKeys = finalJoinList.map(function(item){
      return item.name;
    });

    var allImports = finalJoinList.map(function(item){
      return item.imports;
    });

    var flatImports = allImports.reduce(
        function(a, b) {
          return a.concat(b);
        },
        []
      );

    var toBeIncludedKeys = flatImports.filter(function(item){
      return !(allKeys.indexOf(item) > -1);
    }).unique();


    toBeIncludedKeys.forEach(function(key){
      finalJoinList.push({
      name: key,
      imports: []
    });
    })
    return {finalJoinList:finalJoinList, allJoins: allJoins};
}