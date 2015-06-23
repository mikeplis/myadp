$(document).ready(function() {

  // http://stackoverflow.com/questions/4639372/export-to-csv-in-jquery/13814984#13814984
  jQuery.fn.toCSV = function() {
    var data = $(this).first(); //Only one table
    var csvData = [];
    var tmpArr = [];
    var tmpStr = '';
    data.find("tr").each(function() {
        if($(this).find("th").length) {
            $(this).find("th").each(function() {
              tmpStr = $(this).text().replace(/"/g, '""');
              tmpArr.push('"' + tmpStr + '"');
            });
            csvData.push(tmpArr);
        } else {
            tmpArr = [];
               $(this).find("td").each(function() {
                    if($(this).text().match(/^-{0,1}\d*\.{0,1}\d+$/)) {
                        tmpArr.push(parseFloat($(this).text()));
                    } else {
                        tmpStr = $(this).text().replace(/"/g, '""');
                        tmpArr.push('"' + tmpStr + '"');
                    }
               });
            csvData.push(tmpArr.join(','));
        }
    });
    var output = csvData.join('\n');
    var uri = 'data:application/csv;charset=UTF-8,' + encodeURIComponent(output);
    window.open(uri);
  }

  var rankIdx = 0;
  var nameIdx = 1;
  var posIdx = 2;
  var teamIdx = 3;
  var adpIdx = 4;
  var stdvIdx = 5;

  var tableId = '#data'

  // necessary here until I figure out how to only load main.js on a page with a table (e.g. not the home page)
  if ($(tableId).length > 0) {

    var over = '<div id="overlay">' +
            '<img id="loading" src="/static/images/ajax-loader.gif">' +
            '</div>';
    $(over).appendTo(tableId);

    var t = $(tableId).DataTable({
      "ajax": {
        "url": "/generate",
        "data": apiData // defined in table.html
      },
      "paging": false,
      "scrollCollapse": true,
      // "scrollY": "75%",
      "scrollX": true,
      "dom": 'T<"clear">lrtip',
      "columnDefs": [
        {
          "render": function(data) {
            return data.toFixed(1);
          },
          "targets": [adpIdx, stdvIdx]
        }
      ],
      "tableTools": {
          // "sRowSelect": "os",
          // // if sSelectedClass is changed, must also change selected class in _fnFilterColumn in datatables js file
          // "sSelectedClass": "selected",
          "aButtons": []
      },
      initComplete: function (settings) {
        $('#overlay').hide();

        var api = this.api();
        api.order([adpIdx, 'asc']).draw();


        var searchColumn = function(event) {
          var column = api.column(event.data.idx);
          var val = $.fn.dataTable.util.escapeRegex(
            $(this).val() 
          );
          column
            .search( val ? '^'+val+'$' : '', true, false )
            .draw();
        }

        var fillSelectOptions = function(id, idx) {
          var column = api.column(idx);
          column.data().unique().sort().each(function (d, _) {
            $("#" + id).append( '<option value="'+d+'">'+d+'</option>' )
          });
        }

        fillSelectOptions("positionFilter", posIdx);
        $("#positionFilter").on('change', {'idx': posIdx}, searchColumn);
        
        fillSelectOptions("teamFilter", teamIdx);
        $("#teamFilter").on('change', {'idx': teamIdx}, searchColumn); 
      }
    });


    $("#playerFilter").on("keyup change", function() {
      t.column(nameIdx).search(this.value).draw();
    });

    // creates Rank column
    t.on('order.dt search.dt', function() {
      t.column(rankIdx, {search:'applied', order:'applied'}).nodes().each(function(cell, i) {
        cell.innerHTML = i+1;
      });
    }).draw();

    $(".csv-export").click(function() {
      $("#data").toCSV();
    });
    
  }
});