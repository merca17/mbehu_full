import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node



def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='mbehu_bot' #<--- CHANGE ME

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
    )
    twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params],
            remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')] #'/diff_cont/'
        )
        
    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])
    controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description},
                    controller_params_file]
    )
    # ultrasonico = Node(
    #     package="ultrasinico",
    #     executable="ultrasonic_to_LaserScan",
    #     #parameters=[{'robot_description': robot_description},
    #      #           controller_params_file]
    # )
    # Include the Gazebo launch file, provided by the gazebo_ros package
    delayed_twist_mux = TimerAction(period=3.0, actions=[twist_mux])
    delayed_controller_manager = TimerAction(period=8.0, actions=[controller_manager])
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=["diff_cont"],
    )
    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=["joint_broad"],
    )
    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    # delayed_ultrasonico = TimerAction(period=6.0, actions=[ultrasonico])

    # ultrasonico_spawner = Node(
    #     package="ultrasonico",
    #     executable="ultrasonic_to_LaserScan",
    #     #arguments=["joint_broad"],
    # )
    # delayed_ultrasonico_spawner = RegisterEventHandler(
    #     event_handler=OnProcessStart(
    #         target_action=ultrasonico,
    #         on_start=[ultrasonico_spawner],
    #     )
    # )

    # Launch them all!
    return LaunchDescription([
        rsp,
        delayed_twist_mux,        
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner #,
        # delayed_ultrasonico,
        # delayed_ultrasonico_spawner
    ])