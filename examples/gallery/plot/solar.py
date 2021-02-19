"""
Solar
-----

Use :meth:`pygmt.Figure.solar` to plot the day-night terminator line, 
and civil, nautical, astronomical twilights.
"""
import pygmt

fig = pygmt.Figure()
# Create a figure showing the global region on a Mollweide projection
# Land color is set to dark green and water color is set to light blue
fig.coast(region="d", projection="W0/15c", land="darkgreen", water="lightblue")
# Set a time for the day-night terminator and twilights, 1700 UTC on January 1, 2000
# Set the pen line to be 1p thick
# Set the fill for the night area to be navy blue at 80% transparency
fig.solar(day_night="+d2000-01-01T17:00:00", fill="navyblue@95", pen="1p")
fig.solar(civil_twilight="+d2000-01-01T17:00:00", fill="navyblue@85", pen="1p")
fig.solar(nautical_twilight="+d2000-01-01T17:00:00", fill="navyblue@80", pen="1p")
fig.solar(astronomical_twilight="+d2000-01-01T17:00:00", fill="navyblue@80", pen="1p")
fig.show()