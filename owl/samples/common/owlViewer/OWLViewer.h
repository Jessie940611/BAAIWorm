// ======================================================================== //
// Copyright 2018-2020 Ingo Wald                                            //
//                                                                          //
// Licensed under the Apache License, Version 2.0 (the "License");          //
// you may not use this file except in compliance with the License.         //
// You may obtain a copy of the License at                                  //
//                                                                          //
//     http://www.apache.org/licenses/LICENSE-2.0                           //
//                                                                          //
// Unless required by applicable law or agreed to in writing, software      //
// distributed under the License is distributed on an "AS IS" BASIS,        //
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. //
// See the License for the specific language governing permissions and      //
// limitations under the License.                                           //
// ======================================================================== //

#pragma once

#include "GLFW/glfw3.h"
#ifdef WIN32
#include <windows.h>
#include <gl/GL.h>
#endif
#include <cuda_runtime.h>
#include <cuda_gl_interop.h>
#include "Camera.h"

namespace owl {
  namespace viewer {

    /*! base abstraction for a camera that can generate rays. For this
      viewer, we assume we're dealine with a camera that has a
      rectangular viewing plane that's in focus, and a circular (and
      possible single-point) lens for depth of field. At some later
      point this should also capture time.{t0,t1} for motion blur, but
      let's leave this out for now. */
    struct SimpleCamera
    {
      inline SimpleCamera() {}
      SimpleCamera(const Camera &camera);

      struct {
        vec3f lower_left;
        vec3f horizontal;
        vec3f vertical;
      } screen;
      struct {
        vec3f center;
        vec3f du;
        vec3f dv;
        float radius { 0.f };
      } lens;
    };
    
    /*! snaps a given vector to one of the three coordinate axis;
      useful for pbrt models in which the upvector sometimes isn't
      axis-aligend */
    inline vec3f getUpVector(const vec3f &v)
    {
      int dim = arg_max(abs(v));
      vec3f up(0);
      up[dim] = v[dim] < 0.f ? -1.f : 1.f;
      return up;
    }

    // ------------------------------------------------------------------
    /*! a helper widget that opens and manages a viewer window,
      including some virtual mouse and frame buffer */
    struct OWLViewer {

      static inline vec3f getUpVector(const vec3f &v) { return owl::viewer::getUpVector(v); }

      OWLViewer(const std::string &title = "OWL Sample Viewer",
                const vec2i &initWindowSize=vec2i(1200,800)
                // ,
                // const vec3f &cameraInitFrom = vec3f(0,0,-1),
                // const vec3f &cameraInitAt   = vec3f(0,0,0),
                // const vec3f &cameraInitUp   = vec3f(0,1,0),
                // const float worldScale      = 1.f
                );
      
      /*! window notifies us that we got resized */     
      virtual void resize(const vec2i &newSize);
      
      /*! gets called whenever the viewer needs us to re-render out widget */
      virtual void render() {}
      
      /*! draw framebuffer using OpenGL */
      virtual void draw();

      struct ButtonState {
        bool  isPressed        { false };
        vec2i posFirstPressed  { -1 };
        vec2i posLastSeen      { -1 };
        bool  shiftWhenPressed { false };
        bool  ctrlWhenPressed  { false };
      };

      ButtonState leftButton;
      ButtonState rightButton;
      ButtonState centerButton;
      vec2i       lastMousePosition { -1,-1 };

      /*! this gets called when the window determines that the mouse
        got _moved_ to the given position */
      virtual void mouseMotion(const vec2i &newMousePosition);

      /*! mouse got dragged with left button pressedn, by 'delta'
          pixels, at last position where */
      virtual void mouseDragLeft  (const vec2i &where, const vec2i &delta);
      
      /*! mouse got dragged with left button pressedn, by 'delta'
          pixels, at last position where */
      virtual void mouseDragCenter(const vec2i &where, const vec2i &delta);
      
      /*! mouse got dragged with left button pressedn, by 'delta'
          pixels, at last position where */
      virtual void mouseDragRight (const vec2i &where, const vec2i &delta);
      
      /*! mouse button got either pressed or released at given location */
      virtual void mouseButtonLeft  (const vec2i &where, bool pressed);
      
      /*! mouse button got either pressed or released at given location */
      virtual void mouseButtonCenter(const vec2i &where, bool pressed);
      
      /*! mouse button got either pressed or released at given location */
      virtual void mouseButtonRight (const vec2i &where, bool pressed);

      /*! this gets called when the user presses a key on the keyboard ... */
      virtual void key(char key, const vec2i &/*where*/);
      /*! this gets called when the user presses a 'special' key on
          the keyboard (cursor keys) ... */
      virtual void special(int key, int mods, const vec2i &/*where*/);

      /*! set a new window aspect ratio for the camera, update the
        camera, and notify the app */
      void setAspect(const float aspect)
      {
        camera.setAspect(aspect);
        updateCamera();
      }

      /*! set a new orientation for the camera, update the camera, and
        notify the app */
      void setCameraOrientation(/* camera origin    : */const vec3f &origin,
                                /* point of interest: */const vec3f &interest,
                                /* up-vector        : */const vec3f &up,
                                /* fovy, in degrees : */float fovyInDegrees)
      {
        //camera.setOrientation(origin,interest,up,fovyInDegrees);
        camera.setOrientation(origin,interest,up,fovyInDegrees,false);
        updateCamera();
      }


      void setCameraOptions(float fovy,
                            float focalDistance)

      {
        camera.setFovy(fovy);
        camera.setFocalDistance(focalDistance);

        updateCamera();
      }

      /*! this function gets called whenever any camera manipulator
        updates the camera. gets called AFTER all values have been updated */
      virtual void cameraChanged() {}

      /*! return currently active window size */
      vec2i getWindowSize() const { return fbSize; }
      static vec2i getScreenSize();
      
      Camera &getCamera() { return camera; }
      
      const SimpleCamera getSimplifiedCamera() const
      {
        return SimpleCamera(camera);
      }

      std::shared_ptr<CameraManipulator> cameraManipulator;
      std::shared_ptr<CameraManipulator> inspectModeManipulator;
      std::shared_ptr<CameraManipulator> flyModeManipulator;

      void enableFlyMode();
      enum RotateMode { POI, Arcball };
      void enableInspectMode(RotateMode rm,
                             const box3f &validPoiRange=box3f(),
                             float minPoiDist=1e-3f,
                             float maxPoiDist=std::numeric_limits<float>::infinity());
      void enableInspectMode(const box3f &validPoiRange=box3f(),
                             float minPoiDist=1e-3f,
                             float maxPoiDist=std::numeric_limits<float>::infinity());
      void setWorldScale(const float worldScale)
      {
        camera.motionSpeed = worldScale / sqrtf(6.f);
      }

      /*! re-computes the 'camera' from the 'cameracontrol', and notify
          app that the camera got changed */
      void updateCamera();

      void showAndRun();
      
      void mouseButton(int button, int action, int mods);
      
      /*! the full camera state we are manipulating */
      Camera camera;

      inline vec2i getMousePos() const
      {
        double x,y;
        glfwGetCursorPos(handle,&x,&y);
        return vec2i((int)x, (int)y);
      }
    private:
      friend struct CameraManipulator;
      friend struct CameraInspectMode;
      friend struct CameraFlyMode;

    protected:
      
      vec2i    fbSize { 0 };

      GLuint   fbTexture  {0};
      cudaGraphicsResource_t cuDisplayTexture { 0 };
      uint32_t *fbPointer { nullptr };
      bool shareGraphicResource {true};
      
      /*! the glfw window handle */
      GLFWwindow *handle { nullptr };
      // struct {
      //   bool leftButton { false }, middleButton { false }, rightButton { false };
      // } isPressed;
      vec2i lastMousePos = { -1, -1 };

      uint64_t frameCount{0};
      double   frameTime{ 0 };
      double   fps{ 0 };
      double  totalFrameTime{ 0 };
    };

  } // ::owl::viewer
} // ::owl
