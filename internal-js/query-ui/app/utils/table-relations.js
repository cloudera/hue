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
export default function tableRelations(joinData){

      const allJoins = [];

      joinData.forEach(item =>{
        item.joins.forEach(join =>{
          allJoins.push(join);
        });
      });

      const allJoinsGroupByrightTableId = allJoins.reduce(function (r, a) {
          var x = a.leftTableId.toString() + '-' +  a.rightTableId.toString();
          r[x] = r[x] || [];
          r[x].push(a);
          return r;
      }, Object.create(null));


      const finalConnectionArray = [];
      for (var k in allJoinsGroupByrightTableId) {

        let joinGroupByColumnConnection = allJoinsGroupByrightTableId[k].reduce(function (r, a) {
          var x = a.leftColumnId.toString() + '-' +  a.rightColumnId.toString();
          r[x] = r[x]  || [];
          r[x].push(a);
          return r;
        }, Object.create(null));

        let allConnections = getAllConnections(joinGroupByColumnConnection);
        finalConnectionArray.push({link: k, connections: allConnections});
      }

      var connectionHash = {};
      finalConnectionArray.forEach(connection =>{
        let localObj = {};
        if(!connectionHash[connection.link]){
          localObj = Object.assign(connection);
          connectionHash[connection.link.split('-').reverse().join('-')] = connection.connections;
        } else{
          connectionHash[connection.link] = connection.connections.concat(connectionHash[connection.link])
        }
      })

      var connectedTables = [];
      Object.keys(connectionHash).forEach(function(key) {
        connectedTables.push({ link: key, connections: connectionHash[key]});
      });

      return connectedTables;  

      function getAllConnections(joinGroupByColumnConnection){

        let localAllConnections = [];
        for (var k in joinGroupByColumnConnection) {

            var tempObj = {
              totalJoinCount: 0,
              fullOuterJoinCount: 0,
              innerJoinCount: 0,
              leftOuterJoinCount: 0,
              leftSemiJoinCount: 0,
              rightOuterJoinCount: 0,
            };

            tempObj.id = k;
            tempObj.leftTableId = joinGroupByColumnConnection[k][0].leftTableId;
            tempObj.leftColumnId = joinGroupByColumnConnection[k][0].leftColumnId;
            tempObj.rightTableId = joinGroupByColumnConnection[k][0].rightTableId;
            tempObj.rightColumnId = joinGroupByColumnConnection[k][0].rightColumnId;

            var y = joinGroupByColumnConnection[k].forEach(item => {
              tempObj.totalJoinCount = tempObj.totalJoinCount  + item.totalJoinCount;
              tempObj.fullOuterJoinCount = tempObj.fullOuterJoinCount  + item.fullOuterJoinCount;
              tempObj.innerJoinCount = tempObj.innerJoinCount  + item.innerJoinCount;
              tempObj.leftOuterJoinCount = tempObj.leftOuterJoinCount  + item.leftOuterJoinCount;
              tempObj.leftSemiJoinCount = tempObj.leftSemiJoinCount  + item.leftSemiJoinCount;
              tempObj.rightOuterJoinCount = tempObj.rightOuterJoinCount  + item.rightOuterJoinCount;

            });
            localAllConnections.push(tempObj);
          }

          return localAllConnections;
        }
}