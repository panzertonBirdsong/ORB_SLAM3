//
// Created by slam on 10/27/23.
//

#ifndef ORB_SLAM3_RLPLUGIN_H
#define ORB_SLAM3_RLPLUGIN_H

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <sstream>

#include "Tracking.h"
#include "LocalMapping.h"
#include "LoopClosing.h"

#include "Frame.h"
#include "KeyFrame.h"
#include "sophus/se3.hpp"

#include <mutex>

#include "TCPClient.h"

namespace ORB_SLAM3
{
class System;
class Tracking;
class LocalMapping;
class LoopClosing;

class RLEnvironment
{
public:
    RLEnvironment(System* pSys, Atlas* pAtlas, const float bMonocular, bool bInertial,
                  const string &_strSeqName=std::string());

    void SetTracker(Tracking* pTracker);
    void SetLocalMapper(LocalMapping* pLocalMapper);
    void SetLoopCloser(LoopClosing* pLoopCloser);

    void Run();

    // Collect state
    void CollectImagePixel(cv::Mat &imGrey);
    void CollectImageTimeStamp(const double &timestamp);
    void CollectCurrentFramePose();
    void CollectCurrentFrameTrackMode(const int &nTrackMode);
    void CollectCurrentFrameMatchedInlier(const int &nMatchedInlier);

    void CollectCurrentFramePose(Sophus::SE3f currentTwc);
    void CollectCurrentFrameNumberKeyPoint(int nKeyPoint);
    void CollectCurrentNumberKeyFrame(int keyFrameinMap);

    // Set action
    float GetActionThRefRatio();
    int GetActionMaxFrames();
    int GetActionMinFrames();

protected:
    System *mpSystem;
    Atlas* mpAtlas;
    bool mbMonocular;
    bool mbInertial;
    bool mbFinished;

    bool mbInitialized = false;

    void InitializeRLEnvironment();

    // member pointers to the three main modules
    Tracking* mpTracker;
    bool mbTrackerReady = false;
    LocalMapping* mpLocalMapper;
    LoopClosing* mpLoopCloser;

    //// Timestamp
    std::timed_mutex mMutexImageTimeStamp;
    double mdTimeStamp;

    //// Pixel states
    std::timed_mutex mMutexImagePixel;
    // binary flags for data collection status
    bool mbImageFeaturesReady;
    bool mbCurrentFrameFeaturesReady;

    double CalculateImageEntropy(const cv::Mat& image);
    void CalculateImageFeatures();
    std::timed_mutex mMutexImageFeatures;

    std::timed_mutex mMutexNewFrameProcessed;
    bool mbIsNewFrameProcessed;
    cv::Mat mImGrey;
    // image state
    double mdBrightness;
    double mdLaplacian;
    double mdContrast;
    double mdEntropy;


    //// Tracking states
    void CalculateCurrentFrameFeatures();

    std::timed_mutex mMutexCurrentFrame;
    std::timed_mutex mMutexCurrentFrameFeatures;
    std::timed_mutex mMutexCurrentFrameTrackMode;
    int mnTrackMode;
    std::timed_mutex mMutexCurrentFrameMatchedInlier;
    int mnMatchedInlier;


    std::timed_mutex mMutexCurrentFrameNumberKeyPoint;
    int mnKeyPoint;

    std::timed_mutex mMutexCurrentNumberKeyFrame;
    int mnKeyFrame;

    // Current camera pose in world reference

    std::timed_mutex mMutexCurrentFramePose;

    Sophus::SE3f mTwc;
    // World Pose
    Eigen::Quaternionf mQ; //= Twc.unit_quaternion();
    Eigen::Vector3f mtwc; //= Twc.translation();
    // Relative Pose
    Eigen::Quaternionf mRQ;
    Eigen::Vector3f mRtwc;
    Eigen::Vector3f mREuler;


    std::string msSeqName;
    std::string msCurrentTime;

    // Declare the mFileLogger as an reference using the & operator
    // So that I can copy the actual ofstream to it.
    // Settings of the .csv file
    std::ofstream mFileLogger;
    std::string msCSVFileName;

    void InitializeCSVLogger();
    void InitializeTCPClient(const std::string& serverIP, int serverPort);

    void WriteRowCSVLogger();
    void SendRowTCP();

    void SetTCP2Actions();

    TCPClient* mpTCPClient;

    std::vector<std::string> mvsColumnFeatureNames = {"TimeStamp", "TrackMode", \
                                                   "Brightness", "Contrast", "Entropy", "Laplacian",\
                                                   "MatchedInlier",\
                                                   "NumberKeyPoints", "NumberKeyFrame",\
                                                   "PX", "PY", "PZ", "QX", "QY", "QZ", "QW", \
                                                   "DX", "DY", "DZ", "Yaw", "Pitch", "Roll"};
    float mfActionThRefRatio;
    int mnActionMaxFrames;
    int mnActionMinFrames;
};

// End of the namespace
}

#endif //ORB_SLAM3_RLPLUGIN_H
