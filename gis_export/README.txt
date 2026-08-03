PORT HOUSTON CONTAINER ROUTES — GIS EXPORT
Source: Port Houston Container Service Schedule, revised January 2026.
Coordinate system: WGS84 geographic, EPSG:4326 (.prj included with each shapefile).

CONTENTS
  port_houston_routes_by_service   Polyline. One feature per liner service (its full rotation).
  port_houston_routes_by_leg       Polyline. One feature per port-to-port leg (finer grain).
  port_houston_ports               Point.    One feature per port called.
Each is provided as both a shapefile (.shp/.shx/.dbf/.prj) and a GeoJSON twin
(.geojson — ArcGIS Pro reads these natively and they avoid the shapefile
10-character field-name and 2 GB limits).

FIELDS
  routes_by_service : SVC_ID, NAME, LANE, TEU, TERMINAL, TERM_CODE (BPT/BCT), N_CALLS
  routes_by_leg     : SVC_ID, LANE, SEQ (leg order in rotation), FROM_PORT, TO_PORT, TEU, TERM_CODE
  ports             : PORT_KEY, NAME, LAT, LON, N_SERVICE (services calling), FLAG (interpretation note)

GEOMETRY NOTES
  * Lines are SEA-LANE ROUTES (searoute marine network) following shipping lanes
    through the Panama and Suez canals, Gibraltar and Malacca — not AIS vessel tracks.
  * Trans-Pacific routes are stored as MULTIPART polylines, split at the ±180° antimeridian,
    so no feature slashes horizontally across a world map. In a projected/Pacific-centered
    map you may wish to recombine them.
  * Segments that appear to cross land are canal transits (Panama, Suez) or river approaches
    to inland ports (Manaus/Itacoatiara on the Amazon, New Orleans on the Mississippi).

DATA CAVEATS (see the project METHODOLOGY.md / source.md for full detail)
  * Port coordinates are approximate port locations, adequate for regional/world mapping;
    they are not survey-grade berth positions.
  * A few PDF port names were interpreted; the FLAG field on the ports layer records each.
    The one call most worth verifying with the carrier: LPU's "Panama City" is read here as
    Panama City, FL (Gulf feeder); it could instead be Panama (Pacific).

Regenerate: python build/export_gis.py
