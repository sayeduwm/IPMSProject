import traceback

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.gis.geos import Point
from ipms.forms import EntryForm
from ipms.forms import EntryFormsStaff
from ipms.forms import LeaveSpotForm

from ipms.models import Shapefile
from ipms.models import Feature
from ipms.models import Drivers
from ipms.models import DriversStaff
from ipms.forms import ImportShapefileForm
from ipms.models import SpotCheck
from ipms.models import LeaveSpot
import shapefileIO
import utils

def listShapefiles(request):
    shapefiles = Shapefile.objects.all().order_by('filename')
    return render_to_response("listShapefiles.html", {'shapefiles' : shapefiles})

def importShapefile(request):
    if request.method == "GET":
        form = ImportShapefileForm()
        return render_to_response("importShapefile.html",{'form' : form, 
                                                          'errMsg' : None})
    elif request.method == "POST":
        errMsg = None
        form = ImportShapefileForm(request.POST, request.FILES)
        if form.is_valid():
            shapefile = request.FILES['import_file']
            encoding = request.POST['character_encoding']
            errMsg = shapefileIO.importData(shapefile, encoding)
            if errMsg == None:
                return HttpResponseRedirect("/ipms")
            return render_to_response("importShapefile.html", {'form' : form,
                                                           'errMsg' : errMsg})

def deleteShapefile(request, shapefile_id):
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        raise Http404
    if request.method == "GET":
        return render_to_response("deleteShapefile.html",
                                  {'shapefile' : shapefile})
    elif request.method == "POST":
        if request.POST['confirm'] == "1":
            shapefile.delete()
        return HttpResponseRedirect("/ipms")

def exportShapefile(request, shapefile_id):
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        raise Http404
    return shapefileIO.exportData(shapefile)

def editShapefile(request, shapefile_id):
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        raise Http404
    tmsURL = "http://" + request.get_host() + "/ipms/tms/"
    findFeatureURL = "http://" + request.get_host() + "/ipms/findFeature"
    addFeatureURL = "http://" + request.get_host() + "/ipms/editFeature/" + str(shapefile_id)
    return render_to_response("selectFeature.html",
                              {'shapefile' : shapefile,
                               'findFeatureURL' : findFeatureURL,
                               'addFeatureURL' : addFeatureURL,
                               'tmsURL' : tmsURL})

def findFeature(request):
    try:
        shapefile_id = int(request.GET['shapefile_id'])
        latitude = float(request.GET['latitude'])
        longitude = float(request.GET['longitude'])
        shapefile = Shapefile.objects.get(id=shapefile_id)
        pt = Point(longitude, latitude)
        radius = utils.calcSearchRadius(latitude, longitude, 10)
        
        if shapefile.geom_type == "Point":
            query = Feature.objects.filter(geom_point__dwithin=(pt, radius))
        elif shapefile.geom_type in ["LineString", "MultiLineString"]:
            query = Feature.objects.filter(geom_multilinestring__dwithin=(pt, radius))
        elif shapefile.geom_type in ["Polygon", "MultiPolygon"]:
            query = Feature.objects.filter(geom_multipolygon__dwithin=(pt, radius))
        elif shapefile.geom_type == "MultiPoint":
            query = Feature.objects.filter(geom_multipoint__dwithin = (pt, radius))
        #elif shapefile.geom_type == "GeometryCollection":
            #query = Feature.objects.filter(geom_geometrycollection__dwithin=(pt,radius))
        else:
            print "Unsupported geometry: " + shapefile.geom_type
            return HttpResponse("")
        if query.count() != 1:
            return HttpResponse("")
        
        feature = query.all()[0]
        return HttpResponse("/ipms/editFeature/" +
                    str(shapefile_id)+ "/" + str(feature.id))
    except:
        traceback.print_exc()
        return HttpResponse("")

def editFeature(request, shapefile_id, feature_id=None):
    if request.method == "POST" and "delete" in request.POST:
        return HttpResponseRedirect("/ipms/deleteFeature/" +shapefile_id+
                                    "/"+feature_id)
    
    try:
        shapefile = Shapefile.objects.get(id=shapefile_id)
    except Shapefile.DoesNotExist:
        raise Http404
    if feature_id == None:
        feature = Feature(shapefile=shapefile)
    else:
        try:
            feature = Feature.objects.get(id=feature_id)
        except Feature.DoesNotExist:
            raise Http404
    
    attributes = []
    for attrValue in feature.attributevalue_set.all():
        attributes.append([attrValue.attribute.name, attrValue.value])
    attributes.sort()
    
    geometryField = utils.calcGeometryField(shapefile.geom_type)
    formType = utils.getMapForm(shapefile)
    
    if request.method == "GET":
        wkt = getattr(feature, geometryField)
        form = formType({'geometry' : wkt})
        return render_to_response("editFeature.html", {'shapefile' : shapefile,
                                                       'form' : form,
                                                       'attributes' : attributes})
    elif request.method == "POST":
        form = formType(request.POST)
        try:
            if form.is_valid():
                wkt = form.cleaned_data['geometry']
                setattr(feature, geometryField, wkt)
                feature.save()
                return HttpResponseRedirect("/ipms/edit/" + shapefile_id)
        except ValueError:
            pass
        return render_to_response("editFeature.html", {'shapefile' : shapefile,
                                                       'form' : form,
                                                       'attributes' : attributes})
    
def geolocation(request):
    shapefiles = Shapefile.objects.all().order_by('filename')
    return render_to_response("geolocation.html", {'shapefiles' : shapefiles})

def ipmsindex(request):
    return render_to_response("ipms.html", {'ipmsindex' : ipmsindex})


def studentinstant(request):
    return render_to_response("studentinstant.html", {'studentinstant' : studentinstant})

def staff(request):
    return render_to_response("unastaff.html", {'staff' : staff})


def ins(request):
    form = EntryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        #sms="i am swapon"
    
        
        
        import psycopg2
        con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
        cur = con.cursor()
        orgn=cur.execute("SELECT ST_SetSRID(ST_MakePoint(lon, lat),4326) as the_geom from ipms_requesttest")
        cur.execute("select ipms_stopage.id, ipms_parkingspot.park_name from ipms_stopage, ipms_parkingspot where  st_contains(ipms_stopage.geom, ipms_parkingspot.geom)")
        cur.execute("select ipms_requesttest.lon, ipms_requesttest.lat from ipms_requesttest order by id DESC LIMIT 1")
        for i in cur.fetchall():
            F=str(i[0])+' '+str(i[1])
            print F
        qry="select ipms_stopage.stop from ipms_stopage where  st_contains(ipms_stopage.geom, ST_Transform(ST_GeometryFromText('POINT("+F+ ")',4326),4326 ))"
        print qry
        cur.execute(qry)
        loc=[]
        for i in cur.fetchall():
            loc.append(i)
        #print len(loc)
        if len(loc)==1:
            print "Your Request was not successfull due to you are within "+ str(loc)
            content ="Your Request was not successfull due to you are within "+ str(loc)
            response = HttpResponse(content, content_type='text/plain')
            cur.execute("DELETE FROM ipms_requesttest")
            con.commit()
            return HttpResponse(content, content_type='text/plain')
            
       
        
        else:#...........................
            
            from geolocation.main import GoogleMaps
            from geolocation.distance_matrix.client import DistanceMatrixApiClient
            from osgeo import ogr
            google_maps = GoogleMaps(api_key='AIzaSyBGANydbVz1_vGXu0W1xECXkqGah8joeSk')
            
            try:
                 
                
                #Origin value get=DONE
                cur.execute("insert into ipms_drivers(yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin) select yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin from ipms_requesttest order by ipms_requesttest.id DESC limit 1")
                con.commit()                
                
                cur.execute("SELECT  lat,lon FROM ipms_drivers order by id DESC LIMIT 1"  )
                d=[]
                for orin in cur.fetchall():
                    #print list(orin)
                    p=[str(i) for i in (orin)]
                    q=','.join(p)
                    d.append(q)
                origins=d
                
                # Destination value get=DONE
                cur.execute("SELECT yourstatus FROM ipms_drivers order by id DESC LIMIT 1"  )
                parklist="SELECT  ycord,xcord,park_no FROM ipms_parkinglot where park_use="+"'"+''.join(list(cur.fetchone()))+"'"+ " order by park_no"     
                #print parklist
                cur.execute(parklist)
               
                lot=[]
                for des in cur.fetchall():
                   # print list(des)
                    p=[str(i) for i in (des)[0:2]]
                    q=','.join(p)
                    #print q
                    t=[str(i) for i in (des)[2:3]]
                    w=','.join(t)
                        
                    m=(q,w)
                    lot.append(m)
                    
                
                destinations = lot
                       
                def Traveltime(origins, destinations,no):
                    items = google_maps.distance(origins, destinations)  # default mode parameter is DistanceMatrixApiClient.MODE_DRIVING.
                    f=[]
                    k=[]
                    for item in items:
                        g=item.origin
                        p=((item.duration.days//24*60)+(item.duration.hours*60)+item.duration.minutes+(item.duration.seconds)/60.00)
                        #p=int(item.distance.meters)
                        f.append(p)
                        k.append(g)
                        
                   # k=[i.encode('utf-8') for i in k]
                    return  f 
                
                #calculate travel time by car to parkinglot=Done
                matlist=[]
                cur.execute("SELECT id FROM ipms_drivers order by id DESC LIMIT 1"  )
                did=[str(i) for i in cur.fetchone()]
                q=','.join(did)
                matlist.append(q)    
                for des in  destinations:          
                    driving_time=Traveltime(origins, des[0],des[1]) 
                    cur.execute("SELECT  destination,yourstatus FROM ipms_drivers order by id DESC LIMIT 1"  )
                    dlist=list(cur.fetchone())
                    #print dlist
                    
                    destination_drivers="SELECT "+ ''.join(dlist[0])+ " FROM ipms_parkingspot where park_use=" + "'"+''.join(dlist[1])+ "'" +" and "+"park_no="+str(des[1])+" ORDER BY  park_no ASC, pid ASC"      
                    cur.execute(destination_drivers)          
                    plist=[]  
                    for i in  cur.fetchall():
                        o= list(i)
                        plist=plist+o
                        pl=[driving_time[0]+i for i in plist]
                    #print plist
                    #print pl
                    #print len(pl)
                    matlist=matlist+(pl)
                #print matlist
                
                #print len(matlist)
                #updatecost="INSERT INTO"+''.join(dlist[1])+" VALUES "+ ''.join(matlist)
                #cur.execute(updatecost)
                
                ##update table for creating matrix
                
                
                #print matlist
                
                
                c=tuple(matlist)
                mm="INSERT INTO "+ "ipms_student"+" VALUES"+str(c)
                
                cur.execute(mm)
                
                con.commit() 
            
                
                    
            except psycopg2.DatabaseError, e:
                   print 'Error %s' % e    
                   sys.exit(1)             
            #...............................................
            cur.execute("select ipms_drivers.id from ipms_drivers order by id DESC LIMIT 1")
           
            parkid=[str(z) for z in cur.fetchone()]
            
            content ='Your request has been accepted. Your Id is: '+parkid[0]+ '    .Please store your Id to check your reserved parking spot after 8.00pm'
            response = HttpResponse(content, content_type='text/plain')
            cur.execute("DELETE FROM ipms_requesttest")
            con.commit()             
            
            return HttpResponse(content, content_type='text/plain')      
    return render_to_response('test.html', {'form': form})



def unastaff(request):
    form = EntryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        #sms="i am swapon"
        
        import psycopg2
        con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
        cur = con.cursor()
        orgn=cur.execute("SELECT ST_SetSRID(ST_MakePoint(lon, lat),4326) as the_geom from ipms_requesttest")
        cur.execute("select ipms_stopage.id, ipms_parkingspot.park_name from ipms_stopage, ipms_parkingspot where  st_contains(ipms_stopage.geom, ipms_parkingspot.geom)")
        cur.execute("select ipms_requesttest.lon, ipms_requesttest.lat from ipms_requesttest order by id DESC LIMIT 1")
        for i in cur.fetchall():
            F=str(i[0])+' '+str(i[1])
            print F
        qry="select ipms_stopage.stop from ipms_stopage where  st_contains(ipms_stopage.geom, ST_Transform(ST_GeometryFromText('POINT("+F+ ")',4326),4326 ))"
        print qry
        cur.execute(qry)
        loc=[]
        for i in cur.fetchall():
            loc.append(i)
        #print len(loc)
        if len(loc)==1:
            print "Your Request was not successfull due to you are within "+ str(loc)
            content ="Your Request was not successfull due to you are within "+ str(loc)
            response = HttpResponse(content, content_type='text/plain')
            cur.execute("DELETE FROM ipms_requesttest")
            con.commit()            
            return HttpResponse(content, content_type='text/plain')
            
       
        
        else:#...........................
            cur.execute("insert into ipms_driversstaff(yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin ) select yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin from ipms_requesttest order by ipms_requesttest.id DESC limit 1")
            con.commit()            
            from geolocation.main import GoogleMaps
            from geolocation.distance_matrix.client import DistanceMatrixApiClient
            from osgeo import ogr
            google_maps = GoogleMaps(api_key='AIzaSyBGANydbVz1_vGXu0W1xECXkqGah8joeSk')
            
            try:
                 
                
                #Origin value get=DONE
                cur.execute("SELECT  lat,lon FROM ipms_driversstaff order by id DESC LIMIT 1"  )
                d=[]
                for orin in cur.fetchall():
                    #print list(orin)
                    p=[str(i) for i in (orin)]
                    q=','.join(p)
                    d.append(q)
                origins=d
                
                # Destination value get=DONE
                cur.execute("SELECT yourstatus FROM ipms_driversstaff order by id DESC LIMIT 1"  )
                parklist="SELECT  ycord,xcord,park_no FROM ipms_parkinglot where park_use="+"'"+''.join(list(cur.fetchone()))+"'"+ " order by park_no"     
                #print parklist
                cur.execute(parklist)
               
                lot=[]
                for des in cur.fetchall():
                   # print list(des)
                    p=[str(i) for i in (des)[0:2]]
                    q=','.join(p)
                    #print q
                    t=[str(i) for i in (des)[2:3]]
                    w=','.join(t)
                        
                    m=(q,w)
                    lot.append(m)
                    
                
                destinations = lot
                       
                def Traveltime(origins, destinations,no):
                    items = google_maps.distance(origins, destinations)  # default mode parameter is DistanceMatrixApiClient.MODE_DRIVING.
                    f=[]
                    k=[]
                    for item in items:
                        g=item.origin
                        p=((item.duration.days//24*60)+(item.duration.hours*60)+item.duration.minutes+(item.duration.seconds)/60.00)
                        #p=int(item.distance.meters)
                        f.append(p)
                        k.append(g)
                        
                   # k=[i.encode('utf-8') for i in k]
                    return  f 
                
                #calculate travel time by car to parkinglot=Done
                matlist=[]
                cur.execute("SELECT id FROM ipms_driversstaff order by id DESC LIMIT 1"  )
                did=[str(i) for i in cur.fetchone()]
                q=','.join(did)
                matlist.append(q)    
                for des in  destinations:          
                    driving_time=Traveltime(origins, des[0],des[1]) 
                    cur.execute("SELECT  destination,yourstatus FROM ipms_driversstaff order by id DESC LIMIT 1"  )
                    dlist=list(cur.fetchone())
                    #print dlist
                    
                    destination_drivers="SELECT "+ ''.join(dlist[0])+ " FROM ipms_parkingspot where park_use=" + "'"+''.join(dlist[1])+ "'" +" and "+"park_no="+str(des[1])+" ORDER BY  park_no ASC, pid ASC"      
                    cur.execute(destination_drivers)          
                    plist=[]  
                    for i in  cur.fetchall():
                        o= list(i)
                        plist=plist+o
                        pl=[driving_time[0]+i for i in plist]
                    #print plist
                    #print pl
                    #print len(pl)
                    matlist=matlist+(pl)
                #print matlist
                
                #print len(matlist)
                #updatecost="INSERT INTO"+''.join(dlist[1])+" VALUES "+ ''.join(matlist)
                #cur.execute(updatecost)
                
                ##update table for creating matrix
                
                
                #print matlist
                
                
                c=tuple(matlist)
                mm="INSERT INTO "+ "ipms_una_staff"+" VALUES"+str(c)
                
                cur.execute(mm)
                con.commit()  
                
                    
            except psycopg2.DatabaseError, e:
                   print 'Error %s' % e 
                   import sys
                   sys.exit(1)             
            #...............................................
            cur.execute("select ipms_driversstaff.id from ipms_driversstaff order by id DESC LIMIT 1")
           
            parkid=[str(z) for z in cur.fetchone()]
            
            content ='Your request has been accepted. Your Id is: '+parkid[0]+ '    .Please store your Id to check your reserved parking spot after 8.00pm'
            response = HttpResponse(content, content_type='text/plain')
            cur.execute("DELETE FROM ipms_requesttest")
            con.commit()            
            
            return HttpResponse(content, content_type='text/plain')      
    return render_to_response('unastaff.html', {'form': form})
        
        
        
             
def studentinstant(request):
    form = EntryForm(request.POST or None)
    try:
        import psycopg2
        con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
        cur = con.cursor()
        cur.execute("select pid from ipms_parkingspot where status=1 and park_use='Student'")
        emptyspot=len(cur.fetchall())
        if emptyspot<1:
            return HttpResponse('There is no empty parking spot available now.Try later', content_type='text/plain')
            
        elif request.method == 'POST' and form.is_valid() and emptyspot>=1:
            form.save()
            #sms="i am swapon"
                
            import urllib2
            from BeautifulSoup import BeautifulSoup
            import sys    
            import numpy as np
            
            url ="https://una.transloc.com/t/routes/8002036"
            usock = urllib2.urlopen(url)
            data = usock.read()
            usock.close()
            soup = BeautifulSoup(data)
            tt = soup.findAll('td', {'class': "wait_time"})
            ts = soup.findAll('td', {'class': "stop_name"})
                     
            times=[(td.find('span', {'class':'time_1'})) for td in tt]
            stops=[(td.find('span',{'class': 'stop_name'})) for td in ts]
            
            ttimes=[(span_time_1.text) for span_time_1 in times]
            tstops=[(span_stop_name.text) for span_stop_name in stops] 
            x=[]
            y=[]
            z=[]
            for t in tstops:
                y.append(t)
            for u in ttimes:
                z.append(u)
                          #print ut
            
            for i in np.column_stack((y,z)):
                m= [str(y) for y in i]
                x.append(m)
            print (x)
            
            
            
            
            #############################################################################################################3
            
            
            import psycopg2
            con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
            cur = con.cursor()
            orgn=cur.execute("SELECT ST_SetSRID(ST_MakePoint(lon, lat),4326) as the_geom from ipms_requesttest")
            cur.execute("select ipms_stopage.id, ipms_parkingspot.park_name from ipms_stopage, ipms_parkingspot where  st_contains(ipms_stopage.geom, ipms_parkingspot.geom)")
            cur.execute("select ipms_requesttest.lon, ipms_requesttest.lat from ipms_requesttest order by id DESC LIMIT 1")
            for i in cur.fetchall():
                F=str(i[0])+' '+str(i[1])
                #print F
            qry="select ipms_stopage.stop from ipms_stopage where  st_contains(ipms_stopage.geom, ST_Transform(ST_GeometryFromText('POINT("+F+ ")',4326),4326 ))"
            #print qry
            cur.execute(qry)
            loc=[]
            
            for i in cur.fetchall():
                mstop= [str(y) for y in i]
                loc.append(mstop[0])
            
            #print len(loc)
            print loc
            #print loc,'jjjjjjjjjjjjjjjjjjjjjjjjj'
            
            
            
            ###############################################################################################
            
            
            #print loc,'lllllllllllllllllllll'
            #print p[0]
            if len(loc)>0:
                for i in x:
                    #print i[0],"nnnnnnnnnnnnnnnnnnnnnn"
                    if i[0]==loc[0]:
                        #print "jhjks"
                        #print i
                        #print i[1][:-4]
                        m=int(i[1][:-4][-2:]) 
                        if m<=10 and len(loc)==1:           
                            content= "your request has been discarded due to you are living wintin '"+str(loc[0])+" ' and UNA Shuttle is coming within "+str(m)+' minutes. Please Use UNA Shuttle to make the city more environment friendly'
                            
                            response = HttpResponse(content, content_type='text/plain')
                            cur.execute("DELETE FROM ipms_requesttest")
                            con.commit()            
                           
                            return HttpResponse(content, content_type='text/plain')  
                        else:
                            print"Your Request has been accepted."
                            cur.execute("insert into ipms_studentinstant(yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin ) select yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin  from ipms_requesttest order by ipms_requesttest.id DESC limit 1")
                            con.commit() 
                            con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
                            cur = con.cursor()                
                            from geolocation.main import GoogleMaps
                            from geolocation.distance_matrix.client import DistanceMatrixApiClient
                            from osgeo import ogr
                            google_maps = GoogleMaps(api_key='AIzaSyBGANydbVz1_vGXu0W1xECXkqGah8joeSk')
                            
                            try:
                                 
                                
                                #Origin value get=DONE
                                cur.execute("SELECT  lat,lon FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                                d=[]
                                for orin in cur.fetchall():
                                    #print list(orin)
                                    p=[str(i) for i in (orin)]
                                    q=','.join(p)
                                    d.append(q)
                                origins=d
                                
                                # Destination value get=DONE
                                cur.execute("SELECT yourstatus FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                                parklist="SELECT  ycord,xcord,park_no FROM ipms_parkinglot where park_use="+"'"+''.join(list(cur.fetchone()))+"'"+ " order by park_no"     
                                #print parklist
                                cur.execute(parklist)
                               
                                lot=[]
                                for des in cur.fetchall():
                                   # print list(des)
                                    p=[str(i) for i in (des)[0:2]]
                                    q=','.join(p)
                                    #print q
                                    t=[str(i) for i in (des)[2:3]]
                                    w=','.join(t)
                                        
                                    m=(q,w)
                                    lot.append(m)
                                    
                                
                                destinations = lot
                                       
                                def Traveltime(origins, destinations,no):
                                    items = google_maps.distance(origins, destinations)  # default mode parameter is DistanceMatrixApiClient.MODE_DRIVING.
                                    f=[]
                                    k=[]
                                    for item in items:
                                        g=item.origin
                                        p=((item.duration.days//24*60)+(item.duration.hours*60)+item.duration.minutes+(item.duration.seconds)/60.00)
                                        #p=int(item.distance.meters)
                                        f.append(p)
                                        k.append(g)
                                        
                                   # k=[i.encode('utf-8') for i in k]
                                    return  f 
                                
                                #calculate travel time by car to parkinglot=Done
                                matlist=[]
                                cur.execute("SELECT id FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                                did=[str(i) for i in cur.fetchone()]
                                q=','.join(did)
                                matlist.append(q)    
                                for des in  destinations:          
                                    driving_time=Traveltime(origins, des[0],des[1]) 
                                    cur.execute("SELECT  destination,yourstatus FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                                    dlist=list(cur.fetchone())
                                    #print dlist
                                    
                                    destination_drivers="SELECT "+ ''.join(dlist[0])+ ",ipms_parkingspot.status FROM ipms_parkingspot where park_use=" + "'"+''.join(dlist[1])+ "'" +" and "+"park_no="+str(des[1])+" ORDER BY  park_no ASC, pid ASC"      
                                    cur.execute(destination_drivers)          
                                    plist=[]  
                                    for i in  cur.fetchall():
                                        o= [i[0]*i[1]]
                                        plist=plist+o
                                        pl=[driving_time[0]+i for i in plist]
                                    #print plist
                                    #print pl
                                    #print len(pl)
                                    matlist=matlist+(pl)
                                                           
                                #print matlist
                                
                                #print len(matlist)
                                #updatecost="INSERT INTO"+''.join(dlist[1])+" VALUES "+ ''.join(matlist)
                                #cur.execute(updatecost)
                                
                                ##update table for creating matrix
                                
                                
                                #print matlist
                                
                                
                                c=tuple(matlist)
                                mm="INSERT INTO "+ "ipms_student_instant"+" VALUES"+str(c)
                                
                                cur.execute(mm)
                                con.commit() 
                                con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
                                cur = con.cursor()
                                
                                mat=min(matlist[1:328])
                                ind= matlist.index(mat)
                                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema ='public'AND table_name= 'ipms_student_instant'")
                                    ##print cur.fetchall()[1] 
                                for b in cur.fetchall()[ind]:
                                        print b[2:5]
                                        print b[5:10] 
                                        inp='UPDATE ipms_studentinstant SET pcost='+ str(mat)+','+'parkno='+str(b[2:5])+','+'pid='+str(b[5:10])+' where id='+str(matlist[0])
                                        cur.execute(inp)
                                        prspot='UPDATE ipms_parkingspot SET status=99999'+' where park_no='+str(b[2:5])+' and '+'pid='+str(b[5:10])
                                        cur.execute(prspot)                                        
                                        
                                        chspot='select  ycord,xcord from ipms_parkingspot where park_no='+str(b[2:5])+' and pid='+str(b[5:10])
                                        cur.execute(chspot)
                                        coord=cur.fetchone()
                                        lat=coord[0]
                                        lon=coord[1]
                                        html_str="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 5//EN" "http://www.w3.org/TR/html5/strict.dtd">
                                        <html>
                                        
                                         
                                          <center> <head><font size="6" font color="white"> <b> Get Your Parking Spot Information</b></font></br></br>
                                          <style>
                                
                                    
                                          #map {
                                            width: 500px;
                                            height: 400px;
                                                
                                            border: 2px solid rgba(10, 0, 10, 3);
                                                    
                                          }
                                        </style>
                                        </head>
                                              <body>
                                              <form action="." method="post" enctype="application/x-www-form-urlencoded">
                                                      <tr><th><label for="id_yourid"><font size="6">Your ID:input style="font-size:25px;"</label></th><td><input id="id_yourstatus" name="yourid" input style="font-size:25px;" type="integer" value='' /></td></tr>
                                                       
                                                        <tr><th><label for="id_yourstatus"><font size="6">Your Status:</label></th><td><select id="id_yourstatus" name="yourstatus" input style="font-size:25px;">
                                                        <option value="ipms_drivers" selected="Student">Student</option>
                                                        <option value="ipms_studentinstant">Student Instant</option>
                                                        <option value="ipms_driversstaff">UNA Staff</option>
                                            
                                                    </select></td></tr></br></br>
                                            
                                                    <button type="submit" input style="font-size:25px;">Show My Parking Spot</button>
                                                </form></br>
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
                                                
                                                       
                                                        
                                                        <style>
                                            .center2 {
                                              position: absolute; left: 260px; top: 530px;
                                             
                                                
                                            }
                                            
                                            </style>
                                            
                                            
                                                                                
                                                      
                                                        
                                                        <p1>Your Id = <font color="red">"""+str(matlist[0])+"""</font>. Parking No = <font color="red">"""+str(b[2:5])+"""</font>. Spot No = <font color="red">"""+str(b[5:10])+"""</font> and parking Cost= <font color="red">"""+str(mat)+"""</font> minutes at <i> UNA Main Campus </p1></i>
                                                        <h2>Intelligent parking reservation   system of <i> University of North Alabama</h2></i>
                                                        
                                                
                                                  </body></center>
                                        </html>"""
                                        
                                        Html_file= open(r"C:\geodjango\ipms\templates\rrr.html","w")
                                        Html_file.write(html_str)
                                        print html_str
                                        Html_file.close() 
                                        con.commit()                     
                                        
                                        
                                        cur.execute("DELETE FROM ipms_requesttest")
                                        con.commit()            
                                        
                                        return render_to_response('rrr.html', {'checkreserve': checkreserve})                                                 
    
                            
                            except psycopg2.DatabaseError, e:
                                print 'Error %s' % e 
                                import sys
                                sys.exit(1)                      
            
                        
                   
            else:
                    print"Your Request has been accepted."
                   
                    cur.execute("insert into ipms_studentinstant(yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin ) select yourstatus, lat, lon, destination, rdate, date,parkno,pid,pcost,pprice,pin  from ipms_requesttest order by ipms_requesttest.id DESC limit 1")
                    con.commit() 
                    con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
                    cur = con.cursor()                
                    from geolocation.main import GoogleMaps
                    from geolocation.distance_matrix.client import DistanceMatrixApiClient
                    from osgeo import ogr
                    google_maps = GoogleMaps(api_key='AIzaSyBGANydbVz1_vGXu0W1xECXkqGah8joeSk')
                    
                    try:
                         
                        
                        #Origin value get=DONE
                        cur.execute("SELECT  lat,lon FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                        d=[]
                        for orin in cur.fetchall():
                            #print list(orin)
                            p=[str(i) for i in (orin)]
                            q=','.join(p)
                            d.append(q)
                        origins=d
                        
                        # Destination value get=DONE
                        cur.execute("SELECT yourstatus FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                        parklist="SELECT  ycord,xcord,park_no FROM ipms_parkinglot where park_use="+"'"+''.join(list(cur.fetchone()))+"'"+ " order by park_no"     
                        #print parklist
                        cur.execute(parklist)
                       
                        lot=[]
                        for des in cur.fetchall():
                           # print list(des)
                            p=[str(i) for i in (des)[0:2]]
                            q=','.join(p)
                            #print q
                            t=[str(i) for i in (des)[2:3]]
                            w=','.join(t)
                                
                            m=(q,w)
                            lot.append(m)
                            
                        
                        destinations = lot
                               
                        def Traveltime(origins, destinations,no):
                            items = google_maps.distance(origins, destinations)  # default mode parameter is DistanceMatrixApiClient.MODE_DRIVING.
                            f=[]
                            k=[]
                            for item in items:
                                g=item.origin
                                p=((item.duration.days//24*60)+(item.duration.hours*60)+item.duration.minutes+(item.duration.seconds)/60.00)
                                #p=int(item.distance.meters)
                                f.append(p)
                                k.append(g)
                                
                           # k=[i.encode('utf-8') for i in k]
                            return  f 
                        
                        #calculate travel time by car to parkinglot=Done
                        matlist=[]
                        cur.execute("SELECT id FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                        did=[str(i) for i in cur.fetchone()]
                        q=','.join(did)
                        matlist.append(q)    
                        for des in  destinations:          
                            driving_time=Traveltime(origins, des[0],des[1]) 
                            cur.execute("SELECT  destination,yourstatus FROM ipms_studentinstant order by id DESC LIMIT 1"  )
                            dlist=list(cur.fetchone())
                            #print dlist
                            
                            destination_drivers="SELECT "+ ''.join(dlist[0])+ ",ipms_parkingspot.status FROM ipms_parkingspot where park_use=" + "'"+''.join(dlist[1])+ "'" +" and "+"park_no="+str(des[1])+" ORDER BY  park_no ASC, pid ASC"      
                            cur.execute(destination_drivers)          
                            plist=[]  
                            for i in  cur.fetchall():
                                o= [i[0]*i[1]]
                                plist=plist+o
                                pl=[driving_time[0]+i for i in plist]
                            #print plist
                            #print pl
                            #print len(pl)
                            matlist=matlist+(pl)
                                                   
                        #print matlist
                        
                        #print len(matlist)
                        #updatecost="INSERT INTO"+''.join(dlist[1])+" VALUES "+ ''.join(matlist)
                        #cur.execute(updatecost)
                        
                        ##update table for creating matrix
                        
                        
                        #print matlist
                        
                        
                        c=tuple(matlist)
                        mm="INSERT INTO "+ "ipms_student_instant"+" VALUES"+str(c)
                        
                        cur.execute(mm)
                        con.commit() 
                        con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
                        cur = con.cursor()
                        
                        mat=min(matlist[1:328])
                        ind= matlist.index(mat)
                        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema ='public'AND table_name= 'ipms_student_instant'")
                            ##print cur.fetchall()[1] 
                        for b in cur.fetchall()[ind]:
                                print b[2:5]
                                print b[5:10] 
                                inp='UPDATE ipms_studentinstant SET pcost='+ str(mat)+','+'parkno='+str(b[2:5])+','+'pid='+str(b[5:10])+' where id='+str(matlist[0])
                                cur.execute(inp)
                                prspot='UPDATE ipms_parkingspot SET status=99999'+' where park_no='+str(b[2:5])+' and '+'pid='+str(b[5:10])
                                cur.execute(prspot)                                
                                
                                chspot='select  ycord,xcord from ipms_parkingspot where park_no='+str(b[2:5])+' and pid='+str(b[5:10])
                                cur.execute(chspot)
                                coord=cur.fetchone()
                                lat=coord[0]
                                lon=coord[1]
                                html_str="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 5//EN" "http://www.w3.org/TR/html5/strict.dtd">
                                <html>
           
             <center> <head><font size="6" font color="white"> <b> Get Your Parking Spot Information</b></font></br></br>
                                    <style>
                                
                                  
                                    #map {
                                      width: 500px;
                                      height: 400px;
                                      
                                      border: 2px solid rgba(10, 0, 10, 3);
                                              
                                    }
                                  </style>
                                </head>
                                <body><div class="w3-third">  
                                <form action="." method="post" enctype="application/x-www-form-urlencoded">
                                        <tr><th><label for="id_yourid" ><font size="6">Your ID: </font></label></th><td><input id="id_yourstatus" name="yourid" type="integer" input style="font-size:25px;" value='' /></td></tr>
                                         
                                          <tr><th><label for="id_yourstatus"><font size="6">Your Status:</label></th><td><select id="id_yourstatus" name="yourstatus" input style="font-size:25px;">
                                          <option value="ipms_drivers" selected="Student">Student</option>
                                          <option value="ipms_studentinstant">Student Instant</option>
                                          <option value="ipms_driversstaff">UNA Staff</option>
                              
                                          </select></td></tr></br>
                                  
                                          <button type="submit" input style="font-size:25px;">Show My Parking Spot</button>
                                      </form></br></br>
                                      
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
                              
                                     
                                     
                                     <style>
                         .center2 {
                           position: absolute; left: 260px; top: 530px;
                          
                             
                         }
                         
                         </style>
                                    
                                   <p1>Your Id = <font color="red">"""+str(matlist[0])+"""</font>. Parking No =<font color="red"> """+str(b[2:5])+"""</font>. Spot No =<font color="red"> """+str(b[5:10])+""" </font>and parking Cost= <font color="red">"""+str(mat)+""" </font> minutes at <i> UNA Main Campus </p1></i>
                                    <h2>Intelligent parking reservation   system of <i> University of North Alabama</h2></i>
                                    
                            
                                    </body></center>
                                  </html>"""
                                
                                Html_file= open(r"C:\geodjango\ipms\templates\rrr.html","w")
                                Html_file.write(html_str)
                                print html_str
                                Html_file.close() 
                                con.commit()                     
                                
                                
                                cur.execute("DELETE FROM ipms_requesttest")
                                con.commit()            
                                
                                return render_to_response('rrr.html', {'checkreserve': checkreserve})                                                 
    
                              
                    
                    except psycopg2.DatabaseError, e:
                        print 'Error %s' % e 
                        import sys
                        sys.exit(1)  
        else:
            return render_to_response('studentinstant.html', {'studentinstant': studentinstant})
            
        
        
            
        
        
        
    

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e 
        import sys
        sys.exit(1)        
          
    

        #return render_to_response(sms)
    



def checkreserve(request):
    form = EntryFormsStaff(request.POST or None)
    try: 
        if request.method == 'POST' and form.is_valid():
            form.save()
            import psycopg2
            con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
            cur = con.cursor() 
            cur.execute("select*from ipms_spotcheck order by id desc limit 1")
            p=cur.fetchone()[1]
            cur.execute("select*from ipms_spotcheck order by id desc limit 1")
            q=cur.fetchone()[2]
            
            chspot='select parkno, pid,pcost from '+p+ ' where id='+str(q)
            cur.execute(chspot)
            parkinfo=cur.fetchone()
            park_no=parkinfo[0]
            pid=parkinfo[1]
            print parkinfo 
            pcost=parkinfo[2]

            chspot='select  ycord,xcord from ipms_parkingspot where park_no='+str(park_no)+' and pid='+str(pid)
            cur.execute(chspot)
            coord=cur.fetchone()
            lat=coord[0]
            lon=coord[1]
            html_str="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 5//EN" "http://www.w3.org/TR/html5/strict.dtd">
            <html>
           
             <center> <head><font size="6" font color="white"> <b> Get Your Parking Spot Information</b></font></br></br>
                                    <style>
                                
                                  
                                    #map {
                                      width: 500px;
                                      height: 400px;
                                      
                                      border: 2px solid rgba(10, 0, 10, 3);
                                              
                                    }
                                  </style>
                                </head>
                                <body><div class="w3-third">  
                                <form action="." method="post" enctype="application/x-www-form-urlencoded">
                                        <tr><th><label for="id_yourid" ><font size="6">Your ID: </font></label></th><td><input id="id_yourstatus" name="yourid" type="integer" input style="font-size:25px;" value='' /></td></tr>
                                         
                                          <tr><th><label for="id_yourstatus"><font size="6">Your Status:</label></th><td><select id="id_yourstatus" name="yourstatus" input style="font-size:25px;">
                                          <option value="ipms_drivers" selected="Student">Student</option>
                                          <option value="ipms_studentinstant">Student Instant</option>
                                          <option value="ipms_driversstaff">UNA Staff</option>
                              
                                          </select></td></tr></br>
                                  
                                          <button type="submit" input style="font-size:25px;">Show My Parking Spot</button>
                                      </form></br></br>
                                      
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
                              
                                     
                                     
                                     <style>
                         .center2 {
                           position: absolute; left: 260px; top: 530px;
                          
                             
                         }
                         
                         </style>
        
        
                                             
                  
                    
                         <p1> Your Id = <font color="red">"""+str(q)+"""</font>. Parking No = <font color="red">"""+str(park_no)+"""</font>. Spot No =<font color="red"> """+str(pid)+"""</font> and parking Cost= <font color="red">"""+str(pcost)[0:5]+"""</font> minutes at <i> UNA Main Campus </p1></i>
                         <h2>Intelligent Parking Reservation System of <i> University of North Alabama</h2></i>
                         
                 
                   </body></center>
                 </html>"""
            
            Html_file= open(r"C:\geodjango\ipms\templates\rrr.html","w")
            Html_file.write(html_str)
            print html_str
            Html_file.close() 
            con.commit() 
       
            


        return render_to_response('rrr.html', {'checkreserve': checkreserve}) 
  
         
        
           
            
            
            
    except:
                
                content="Please input all the necessary information correctly."
                return HttpResponse(content, content_type='text/plain')                   
                 
        #return render_to_response('rrr.html', {'checkreserve': checkreserve}) 
           
    
     
        
def leavespot(request):
    form = LeaveSpotForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()    
        
        import psycopg2
        con = psycopg2.connect(database='geodjango', user='postgres', password= '143143')
        cur = con.cursor() 
        try:
            cur.execute("select*from ipms_leavespot order by id desc limit 1")
            p=cur.fetchone()[1]
            cur.execute("select*from ipms_leavespot order by id desc limit 1")
            q=cur.fetchone()[2]
            cur.execute("select*from ipms_leavespot order by id desc limit 1")
            r=cur.fetchone()[3]            
            print p,q,r
            chspot='select parkno, id, pin,pid from '+q+ ' where id='+str(p)
            cur.execute(chspot)
            spotinfo=cur.fetchone()
            park_no=spotinfo[0]
            ps=spotinfo[1]
            ppin=spotinfo[2]
            pid=spotinfo[3]
            print ps,ppin,park_no,pid
            if p==ps and r==ppin:
                
                chspot='UPDATE ipms_parkingspot SET status=1 WHERE park_no='+ str(park_no)+' and pid='+str(pid)
                cur.execute(chspot)
                pk='plodng@1'+str(ppin)
                chpin='update '+q+ ' set pin='+"'"+pk+"'"+' where parkno='+ str(park_no)+' and pid='+str(pid)
                #cur.execute('update ipms_drivers set pin=6 where parkno=6 and pid=76')   
                cur.execute(chpin)
                cur.execute("DELETE FROM ipms_leavespot")
                con.commit()
                content='You have left your assinged Parking Spot successfully. Thank you for being with us'
                return HttpResponse(content, content_type='text/plain') 
            else: 
                cur.execute("DELETE FROM ipms_leavespot")
                content='Not Fond. Please input all the values Correctly '
                
                return HttpResponse(content, content_type='text/plain')             
           
        except:
            cur.execute("DELETE FROM ipms_leavespot")
            content='Not Found.Please input all the values Correctly '       
            return HttpResponse(content, content_type='text/plain')  
        
                
    return render_to_response('leavespot.html', {'checkreserve': checkreserve})