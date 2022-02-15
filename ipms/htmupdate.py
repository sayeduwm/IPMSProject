import psycopg2
con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
cur = con.cursor() 
cur.execute("select*from ipms_spotcheck order by id desc limit 1")
p=cur.fetchone()[1]
cur.execute("select*from ipms_spotcheck order by id desc limit 1")
q=cur.fetchone()[2]

chspot='select parkno, pid from '+p+ ' where id='+str(q)
cur.execute(chspot)
parkinfo=cur.fetchone()
park_no=parkinfo[0]
pid=parkinfo[1]
print parkinfo


chspot='select  ycord,xcord from ipms_parkingspot where park_no='+str(park_no)+' and pid='+str(pid)
cur.execute(chspot)
coord=cur.fetchone()
lat=coord[0]
lon=coord[1]
print lat,lon 



html_str="""<!DOCTYPE html>
<html>
  <head>
    <style>

    
      #map {
        width: 500px;
        height: 400px;
        position: absolute; left: 430px; top: 100px;
        border: 2px solid rgba(10, 0, 10, 3);
                
      }
    </style>
  </head>
  <body>
<td xcord='lat'>
<td  ycord='lon'>

    <div id="map"></div>
    <script>
      function initMap() {
        var mapDiv = document.getElementById('map');
        var map = new google.maps.Map(mapDiv, {
          center: {lat: """+str(lat)+""", lng: """+str(lon)+"""},
          mapTypeId:google.maps.MapTypeId.SATELLITE,
          zoom: 20
        });

        var marker = new google.maps.Marker({
          position: {lat: """+str(lat)+""", lng: """+str(lon)+"""},
          map: map,
          title: 'Hello World!'
          
        });
       
      }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?callback=initMap"
        async defer></script>


       <body style="background-color:#9966FF;">

       <form action="." method="post" enctype="application/x-www-form-urlencoded">
          <tr><th><label for="id_yourid">Your ID:</label></th><td><input id="id_yourstatus" name="yourid" type="integer" value='' /></td></tr>
           
            <tr><th><label for="id_yourstatus">Your Status:</label></th><td><select id="id_yourstatus" name="yourstatus">
            <option value="ipms_drivers" selected="Student">Student</option>
            <option value="ipms_studentinstant">Student Instant</option>
            <option value="ipms_driversstaff">UNA Staff</option>

            </select></td></tr>
    
            <button type="submit">Show My Parking Spot</button>
        </form>



  </body>
</html>"""

Html_file= open(r"C:\geodjango\ipms\templates\rrrr.html","w")
Html_file.write(html_str)
print html_str
Html_file.close()