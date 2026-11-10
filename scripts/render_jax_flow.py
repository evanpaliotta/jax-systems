import bpy, math, os, sys, argparse
from mathutils import Vector
from random import Random

p=argparse.ArgumentParser();p.add_argument('out');p.add_argument('--still',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);os.makedirs(a.out,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='BLENDER_EEVEE';S.render.resolution_x=1200;S.render.resolution_y=675;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.film_transparent=False;S.render.fps=24;S.frame_start=1;S.frame_end=96
S.world.color=(.18,.18,.18);S.view_settings.view_transform='AgX'
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*c,1);q.inputs['Roughness'].default_value=.32;q.inputs['Metallic'].default_value=metal;return m
T=mat('Ceramic teal',(0,.155,.185));G=mat('Brushed gold',(.68,.43,.075),.65);B=mat('Soft black',(.018,.026,.032));W=mat('Warm porcelain',(.89,.88,.80));C=mat('Sand',(.60,.55,.43))
def finish(o,m,bev=0):
 o.data.materials.append(m)
 if bev:
  b=o.modifiers.new('Soft machined edges','BEVEL');b.width=bev;b.segments=4
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def box(n,loc,sc,m,bev=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.scale=sc;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,m,bev)
def uv(n,loc,sc,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=n;o.scale=sc;return finish(o,m)
def cyl(n,loc,r,d,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d,location=loc,rotation=rot);return finish(bpy.context.object,m,.035)
def tube(n,pts,r,m,cyclic=False):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=4;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for q,v in zip(s.points,pts):q.co=(*v,1)
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def path(t):
 # enquiry -> context gate -> approval, smooth closed conveyor
 u=2*math.pi*t
 if t<.5:
  v=t*2;x=-4.7+9.4*v;z=1.0+.48*math.sin(math.pi*v)
 else:
  v=(t-.5)*2;x=4.7-9.4*v;z=.48+.30*math.sin(math.pi*v)
 return Vector((x,.12*math.sin(u),z))
def lin(o):
 if o.animation_data and o.animation_data.action:
  for f in (o.animation_data.action.fcurves if hasattr(o.animation_data.action,'fcurves') else [f for layer in o.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]):
   for k in f.keyframe_points:k.interpolation='LINEAR'
box('Seamless floor',(0,0,-.52),(200,200,.1),W,.02)
# coastal contour island
box('Monolithic porcelain island',(0,0,-.22),(12.2,6.2,.44),W,.28)
for j in range(3):
 pts=[(-5.7+11.4*i/100,-2.45+j*.34+.18*math.sin(i/100*math.pi*2+j),.035) for i in range(101)]
 tube('Coastal contour',pts,.025,C)
# left: recognizable telephone handset resting in sculpted dock
box('Enquiry dock',(-4.25,0,.30),(2.05,1.75,.60),T,.22)
for x in (-4.92,-3.58):box('Dock cradle',(x,0,.72),(.34,1.12,.42),B,.13)
pts=[]
for i in range(61):
 t=math.pi*i/60;pts.append((-4.25+.77*math.cos(t),0,1.02+.40*math.sin(t)))
tube('Handset grip',pts,.19,B)
for x in (-5.02,-3.48):
 o=uv('Handset earpiece',(x,0,1.02),(.34,.38,.25),B)
 cyl('Gold acoustic inset',(x,-.34,1.02),.15,.035,G,(math.pi/2,0,0))
# center: precision context arch and card sorting throat
for x in (-1.25,1.25):box('Arch foot',(x,0,.32),(.70,1.60,.64),T,.18)
pts=[(1.25*math.cos(math.pi*i/80),0,1.0+2.25*math.sin(math.pi*i/80)) for i in range(81)]
tube('Context arch',pts,.24,T)
box('Sorting throat',(0,0,1.12),(1.65,1.05,.24),B,.09)
for x in (-.57,.57):box('Gold guide',(x,-.58,1.48),(.10,.12,.68),G,.04)
for i in range(3):
 o=box('Context card',(-.18+i*.18,.12,1.72+i*.12),(1.12,.10,.72),W,.055);o.rotation_euler[1]=-.12+i*.12
# right: organized brief fan and standing approval tile
box('Handoff plinth',(4.15,0,.25),(2.25,1.85,.50),T,.20)
for i in range(4):
 o=box('Brief sheet',(3.65,.18,.61+i*.055),(1.25,1.05,.055),W,.025);o.rotation_euler[2]=-.20+i*.12
box('Approval card',(4.65,.12,1.55),(1.18,.24,1.75),W,.16)
box('Approval black header',(4.65,-.025,2.15),(.78,.055,.12),B,.035)
# raised gold checkmark
tube('Approval check',[(4.28,-.055,1.52),(4.53,-.055,1.28),(5.02,-.055,1.83)],.075,G)
# flow rails and moving gold signal tokens
for off in (0,.5):
 pts=[tuple(path(i/240)+Vector((0,off*.0,-.12))) for i in range(241)]
 tube('Porcelain flow guide',pts,.045,C,True)
for j in range(7):
 o=uv('Gold signal',(0,0,0),(.13,.13,.13),G)
 for f in range(1,98,4):
  o.location=path(((f-1)/96+j/7)%1);o.keyframe_insert('location',frame=f)
 o.location=path(j/7);o.keyframe_insert('location',frame=97);lin(o)
# purposeful sorting paddle and approval breathing motion
paddle=box('Sorting paddle',(0,-.48,1.92),(1.25,.12,.12),G,.045)
for f in range(1,98,4):
 t=2*math.pi*(f-1)/96;paddle.rotation_euler[1]=.16*math.sin(t*3);paddle.keyframe_insert('rotation_euler',frame=f)
lin(paddle)
# lighting/camera
def area(n,loc,power,size,color):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-4,-6,10),1500,7,(1,.91,.78));area('Fill',(6,-2,7),1050,6,(.78,.91,1));area('Rim',(1,5,9),1800,5,(1,.94,.82));area('Front',(0,-8,4),350,5,(1,1,1))
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);bpy.context.collection.objects.link(cam);cam.location=(11,-17,12);target=Vector((0,0,1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=15.4;S.camera=cam
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.72,.66,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.45
S.render.filepath=os.path.join(a.out,'poster.png' if a.still else 'frame_');S.frame_set(24 if a.still else 1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out,'jax_workshop.blend'))
if a.still:bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
