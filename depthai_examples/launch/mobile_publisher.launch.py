import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, launch_description_sources
from launch.actions import IncludeLaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import launch_ros.actions
import launch_ros.descriptions
from launch_ros.parameter_descriptions import ParameterValue 

def generate_launch_description():
    default_rviz = os.path.join(get_package_share_directory('depthai_examples'),
                                'rviz', 'pointCloud.rviz')
    urdf_launch_dir = os.path.join(get_package_share_directory('depthai_bridge'), 'launch')
    
    camera_model     = LaunchConfiguration('camera_model',  default = 'OAK-D')
    tf_prefix        = LaunchConfiguration('tf_prefix',   default = 'oak')
    base_frame       = LaunchConfiguration('base_frame',    default = 'oak-d_frame')
    parent_frame     = LaunchConfiguration('parent_frame',  default = 'oak-d-base-frame')
    cam_pos_x        = LaunchConfiguration('cam_pos_x',     default = '0.0')
    cam_pos_y        = LaunchConfiguration('cam_pos_y',     default = '0.0')
    cam_pos_z        = LaunchConfiguration('cam_pos_z',     default = '0.0')
    cam_roll         = LaunchConfiguration('cam_roll',      default = '0.0')
    cam_pitch        = LaunchConfiguration('cam_pitch',     default = '0.0')
    cam_yaw          = LaunchConfiguration('cam_yaw',       default = '0.0')

    camera_param_uri = LaunchConfiguration('camera_param_uri', default = 'package://depthai_examples/params/camera')
    sync_nn          = LaunchConfiguration('sync_nn', default = True)
    nn_path          = LaunchConfiguration('nn_path', default = "")


    declare_camera_model_cmd = DeclareLaunchArgument(
        'camera_model',
        default_value=camera_model,
        description='The model of the camera. Using a wrong camera model can disable camera features. Valid models: `OAK-D, OAK-D-LITE`.')

    declare_tf_prefix_cmd= DeclareLaunchArgument(
        'tf_prefix',
        default_value=tf_prefix,
        description='The name of the camera. It can be different from the camera model and it will be used in naming TF.')

    declare_base_frame_cmd = DeclareLaunchArgument(
        'base_frame',
        default_value=base_frame,
        description='Name of the base link.')

    declare_parent_frame_cmd = DeclareLaunchArgument(
        'parent_frame',
        default_value=parent_frame,
        description='Name of the parent link from other a robot TF for example that can be connected to the base of the OAK.')

    declare_pos_x_cmd = DeclareLaunchArgument(
        'cam_pos_x',
        default_value=cam_pos_x,
        description='Position X of the camera with respect to the base frame.')

    declare_pos_y_cmd = DeclareLaunchArgument(
        'cam_pos_y',
        default_value=cam_pos_y,
        description='Position Y of the camera with respect to the base frame.')

    declare_pos_z_cmd = DeclareLaunchArgument(
        'cam_pos_z',
        default_value=cam_pos_z,
        description='Position Z of the camera with respect to the base frame.')

    declare_roll_cmd = DeclareLaunchArgument(
        'cam_roll',
        default_value=cam_roll,
        description='Roll orientation of the camera with respect to the base frame.')

    declare_pitch_cmd = DeclareLaunchArgument(
        'cam_pitch',
        default_value=cam_pitch,
        description='Pitch orientation of the camera with respect to the base frame.')

    declare_yaw_cmd = DeclareLaunchArgument(
        'cam_yaw',
        default_value=cam_yaw,
        description='Yaw orientation of the camera with respect to the base frame.')

    declare_camera_param_uri_cmd = DeclareLaunchArgument(
        'camera_param_uri',
        default_value=camera_param_uri,
        description='Sending camera yaml path')

    declare_sync_nn_cmd = DeclareLaunchArgument(
        'sync_nn',
        default_value=sync_nn,
        description='Syncs the image output with the Detection.')

    declare_nn_path_cmd = DeclareLaunchArgument(
        'nn_path',
        default_value=nn_path,
        description='Path to the object detection blob needed for detection')

    mobilenet_node = launch_ros.actions.Node(
            package='depthai_examples', executable='mobilenet_node',
            output='screen',
            parameters=[{'tf_prefix': tf_prefix},
                        {'camera_param_uri': camera_param_uri},
                        {'sync_nn': sync_nn},
                        {'nn_path': nn_path}])

    metric_converter_node = launch_ros.actions.ComposableNodeContainer(
            name='container',
            namespace='',
            package='rclcpp_components',
            executable='component_container',
            composable_node_descriptions=[
                # Driver itself
                launch_ros.descriptions.ComposableNode(
                    package='depth_image_proc',
                    plugin='depth_image_proc::ConvertMetricNode',
                    name='convert_metric_node',
                    remappings=[('image_raw', '/stereo/depth'),
                                ('camera_info', '/stereo/camera_info'),
                                ('image', '/stereo/converted_depth')]
                ),
            ],
            output='screen',)

    point_cloud_node = launch_ros.actions.ComposableNodeContainer(
            name='container2',
            namespace='',
            package='rclcpp_components',
            executable='component_container',
            composable_node_descriptions=[
                # Driver itself
                launch_ros.descriptions.ComposableNode(
                    package='depth_image_proc',
                    plugin='depth_image_proc::PointCloudXyziNode',
                    name='point_cloud_xyzi',

                    remappings=[('depth/image_rect', '/stereo/converted_depth'),
                                ('intensity/image_rect', '/right/image_rect'),
                                ('intensity/camera_info', '/right/camera_info'),
                                ('points', '/stereo/points')]
                ),
            ],
            output='screen',)

    ld = LaunchDescription()
    ld.add_action(declare_tf_prefix_cmd)
    ld.add_action(declare_camera_model_cmd)

    ld.add_action(declare_base_frame_cmd)
    ld.add_action(declare_parent_frame_cmd)

    ld.add_action(declare_pos_x_cmd)
    ld.add_action(declare_pos_y_cmd)
    ld.add_action(declare_pos_z_cmd)
    ld.add_action(declare_roll_cmd)
    ld.add_action(declare_pitch_cmd)
    ld.add_action(declare_yaw_cmd)

    ld.add_action(declare_camera_param_uri_cmd)
    ld.add_action(declare_sync_nn_cmd)
    ld.add_action(declare_nn_path_cmd)

    ld.add_action(mobilenet_node)

    #ld.add_action(metric_converter_node)
    #ld.add_action(point_cloud_node)
    # ld.add_action(rviz_node)
    return ld

