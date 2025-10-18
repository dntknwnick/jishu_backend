require_relative '../node_modules/react-native/scripts/react_native_pods'
require_relative '../node_modules/@react-native-community/cli-platform-ios/native_modules'

platform :ios, '13.4'

target 'JishuMobile' do
  use_react_native!(
    :path => '../node_modules/react-native',
    # Hermes is now enabled by default.
    :hermes_enabled => true,
    :fabric_enabled => false,
    # An absolute path to your application root.
    :app_path => "#{Pod::Config.instance.installation_root}/.."
  )

  pod 'RNVectorIcons', :path => '../node_modules/react-native-vector-icons'
  pod 'BVLinearGradient', :path => '../node_modules/react-native-linear-gradient'

  target 'JishuMobileTests' do
    inherit! :complete
    # Pods for testing
  end

  post_install do |installer|
    # https://github.com/facebook/react-native/blob/main/packages/react-native/scripts/react_native_pods.rb#L197-L202
    react_native_post_install(
      installer,
      '../node_modules/react-native',
      :mac_catalyst_enabled => false
    )
    __apply_Xcode_12_5_M1_post_install_workaround(installer)
  end
end
