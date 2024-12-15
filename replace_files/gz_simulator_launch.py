import os
from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument,SetEnvironmentVariable
from launch_ros.actions import Node
import launch_ros.descriptions
from launch_ros.parameter_descriptions import ParameterValue
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from pathlib import Path
from launch.conditions import IfCondition

def generate_launch_description():
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    urdf_file= LaunchConfiguration('urdf_file')
    # Check if we're told to use sim time
    use_sim_time = LaunchConfiguration('use_sim_time')
    bringup_dir = get_package_share_directory('lesson_urdf')
    world = os.path.join(bringup_dir , "world", "depot.sdf")
    
    start_robot_state_publisher_cmd = Node(
        condition=IfCondition(use_robot_state_pub),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[urdf_file])

    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join([
            os.path.join(bringup_dir, 'world'),
            str(Path(bringup_dir).parent.resolve())
        ])
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory("ros_gz_sim"),
                    "launch",
                    "gz_sim.launch.py",
                )
            ]
        ),
        launch_arguments={"gz_args": ["-r -v 4 ", world]}.items(),
    )

    # Spawn the robot in Gazebo
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            "robot1",
            "-topic",
            "/robot_description",
            "-x",
            "0",
            "-y",
            "0",
            "-z",
            "10.4",
        ],
        output="screen",
    )
    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time',default_value='true',description='Use sim time if true'),
        DeclareLaunchArgument('urdf_file',default_value=os.path.join(bringup_dir, 'urdf', 'planar_3dof.urdf'),description='Whether to start RVIZ'),
        DeclareLaunchArgument('use_robot_state_pub',default_value='True',description='Whether to start the robot state publisher'),
        gz_resource_path,
        gz_sim, spawn_entity,start_robot_state_publisher_cmd
    ])