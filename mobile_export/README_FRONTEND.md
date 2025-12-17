# Hitbox Detection on iOS with Expo

This folder contains the **optimized YOLO11 model** (`yolo11n-seg_int8.tflite`) ready for your React Native/Expo app.

## 1. Installation

In your Expo project, install these **two** libraries. This combination is the easiest way to run CoreML/TFLite models without writing Swift code.

```bash
npm install react-native-vision-camera react-native-fast-tflite
```

## 2. Configure `app.json`

Add the plugins to your Expo config. This enables the **CoreML Delegate** (Apple Neural Engine) so the model runs instantly.

```json
{
  "expo": {
    "plugins": [
      [
        "react-native-vision-camera",
        {
          "enableMicrophonePermission": true
        }
      ],
      [
        "react-native-fast-tflite",
        {
          "enableCoreMLDelegate": true
        }
      ]
    ]
  }
}
```

## 3. Usage Code (React Native)

Create a component (e.g., `HitboxCamera.tsx`).

**Key Steps:**
1. Load the model using `useTensorflowModel`.
2. Use `useFrameProcessor` to run the model on every camera frame.
3. Draw the results (boxes/polygons) on the screen.

```tsx
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Camera, useCameraDevice, useFrameProcessor } from 'react-native-vision-camera';
import { useTensorflowModel, TensorflowModel } from 'react-native-fast-tflite';
import { useResizePlugin } from 'vision-camera-resize-plugin'; // Optional: helps resize frame if needed

export function HitboxCamera() {
  const device = useCameraDevice('back');
  
  // 1. Load the model file (put the .tflite file in your assets or download it)
  // Note: For local assets, you might need to bundle it using `expo-asset` or similar
  const model = useTensorflowModel(require('./assets/yolo11n-seg_int8.tflite'));

  // 2. Run on every frame
  const frameProcessor = useFrameProcessor((frame) => {
    'worklet';
    if (model.state !== 'loaded') return;

    // Run the model
    const results = model.model.runSync([frame]);
    
    // The 'results' array contains the raw output tensors from YOLO.
    // Index 0: Boxes/Masks
    // You will need to parse these raw numbers into coordinates.
    const detections = results[0]; 
    console.log(`Detected ${detections.length} objects`);
    
  }, [model]);

  if (device == null) return <Text>No Camera</Text>;

  return (
    <Camera
      style={StyleSheet.absoluteFill}
      device={device}
      isActive={true}
      frameProcessor={frameProcessor}
      pixelFormat="yuv" // Required for TFLite
    />
  );
}
```

## 4. Build

Because this uses native code (CoreML), **you cannot use Expo Go**. You must create a development build:

```bash
npx expo prebuild
npx expo run:ios
```

## Model Details
- **File**: `yolo11n-seg_int8.tflite`
- **Architecture**: YOLO11 Nano Segmentation
- **Optimization**: Int8 Quantization (4x smaller, ~2x faster on iPhone)
- **Input Size**: 640x640
