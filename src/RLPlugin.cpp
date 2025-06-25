//
// Created by Tianyi on 10/27/23.
//

#include "RLPlugin.h"
#include "TCPClient.h"

namespace ORB_SLAM3
{
RLEnvironment::RLEnvironment(System* pSys, Atlas *pAtlas, const float bMonocular, bool bInertial, const string &_strSeqName)
{
    mbMonocular = bMonocular;
    mbInertial = bInertial;
    mpSystem = pSys;
    mpAtlas = pAtlas;
    //msSeqName = _strSeqName;

    InitializeRLEnvironment();
}

void RLEnvironment::InitializeRLEnvironment()
{
    // Initialize variables
    mbFinished = false;
    mpTracker = NULL;
    mpLocalMapper = NULL;
    mpLoopCloser = NULL;
    mdTimeStamp = 0.0;
    mbImageFeaturesReady = false;
    mbCurrentFrameFeaturesReady = false;
    mbIsNewFrameProcessed = true;
    mdBrightness = 0.0;
    mdLaplacian = 0.0;
    mdContrast = 0.0;
    mdEntropy = 0.0;
    mnTrackMode = 0;
    mnMatchedInlier = 0.0;
    mnKeyPoint = 0;

    mfActionThRefRatio = 0.9f;
    mnActionMaxFrames = 30;
    mnActionMinFrames = 0;

    // Initialize IO
    InitializeCSVLogger();
    InitializeTCPClient("127.0.0.1", 10000);

    // Initialization Done
    mbInitialized = true;
    std::cout << " Reinforcement Learning Plugin Initialized" << std::endl;
    std::cout << std::endl;
}

void RLEnvironment::SetTracker(Tracking *pTracker)
{
    mpTracker = pTracker;
    mbTrackerReady = true;
}

void RLEnvironment::SetLocalMapper(LocalMapping *pLocalMapper)
{
    mpLocalMapper = pLocalMapper;
}

void RLEnvironment::SetLoopCloser(LoopClosing *pLoopCloser)
{
    mpLoopCloser = pLoopCloser;
}


void RLEnvironment::Run()
{
    while(true)
    {
        if(mbTrackerReady)
        {
            if(mbIsNewFrameProcessed == false)
            {
                CalculateImageFeatures();
                //std::cout << " RL plugin - Run - Time Stamp @ " << fixed << setprecision(6) << mdTimeStamp << std::endl;
                //std::cout << " RL plugin - Run - laplacian @ " << fixed << setprecision(2) << mdLaplacian << std::endl;
                //std::cout << " RL plugin - Run - TrackMode @ " << mnTrackMode << std::endl;
                //std::cout << " RL plugin - Run - MatchedInlier @ " << mnMatchedInlier << std::endl;
                //std::cout << " RL plugin - Run - Coordinates @ " << fixed << setprecision(2) << mtwc(0) << "," <<  mtwc(1) << "," <<  mtwc(2) << std::endl;

                WriteRowCSVLogger();
                SendRowTCP();
                SetTCP2Actions();

                //// flip the flag of mbIsNewFrameProcessed
                // Try to acquire the timed_mutex with a timeout of 1 milliseconds
                if (mMutexNewFrameProcessed.try_lock_for(std::chrono::milliseconds(1))) {
                    mbIsNewFrameProcessed = true;
                    mMutexNewFrameProcessed.unlock();
                }
                else {
                    std::cout << " failed to acquire the mMutexNewFrameProcessed within 1 milliseconds." << std::endl;
                }
            }
        }
        // Wait for 0.01s = 10ms
        usleep(0.01*1000*1000);
    }
}


void RLEnvironment::CollectImageTimeStamp(const double &timestamp)
{
    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexImageTimeStamp.try_lock_for(std::chrono::milliseconds(1))) {
        mdTimeStamp = timestamp;
        mMutexImageTimeStamp.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexImageTimeStamp within 1 milliseconds." << std::endl;
    }
}

void RLEnvironment::CollectImagePixel(cv::Mat &imGrey)
{
    // Try to acquire the mMutexImagePixel with a timeout of 1 milliseconds
    if (mMutexImagePixel.try_lock_for(std::chrono::milliseconds(1))) {
        //Option1: save the image with the same resolution
        mImGrey = imGrey.clone();

        //Option2: save the image with reduced resolution (reduced by 1/16 = 1/4*1/4)
        //cv::resize(imGrey, mImGrey, cv::Size(), 0.25, 0.25, cv::INTER_NEAREST);
        // Instead, reduce the image resolution later at the calculation step
        mMutexImagePixel.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexImagePixel within 1 milliseconds." << std::endl;
    }

    // update the data ready flag
    mbImageFeaturesReady = true;

    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexNewFrameProcessed.try_lock_for(std::chrono::milliseconds(1))) {
        mbIsNewFrameProcessed = false;
        mMutexNewFrameProcessed.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexNewFrameProcessed within 1 milliseconds." << std::endl;
    }
}

void RLEnvironment::CollectCurrentFrameTrackMode(const int &nTrackMode)
{
    //    SYSTEM_NOT_READY=-1,
    //    NO_IMAGES_YET=0,
    //    NOT_INITIALIZED=1,
    //    OK=2,
    //    RECENTLY_LOST=3,
    //    LOST=4,
    //    OK_KLT=5

    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexCurrentFrameTrackMode.try_lock_for(std::chrono::milliseconds(1))) {
        mnTrackMode = nTrackMode;
        if(nTrackMode == 2)
        {
            mbCurrentFrameFeaturesReady = true;
        }
        else
        {
            mbCurrentFrameFeaturesReady = false;
        }
        mMutexCurrentFrameTrackMode.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexCurrentFrameTrackMode within 1 milliseconds." << std::endl;
    }
}

void RLEnvironment::CollectCurrentFrameMatchedInlier(const int &nMatchedInlier)
{
    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexCurrentFrameMatchedInlier.try_lock_for(std::chrono::milliseconds(1))) {
        mnMatchedInlier = nMatchedInlier;
        mMutexCurrentFrameMatchedInlier.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexCurrentFrameMatchedInlier within 1 milliseconds." << std::endl;
    }
}

double RLEnvironment::CalculateImageEntropy(const cv::Mat& image)
{
    // Calculate histogram of pixel intensities
    cv::Mat hist;
    int histSize = 256;  // Number of bins for intensity values
    float range[] = {0, 256};
    const float* histRange = {range};
    cv::calcHist(&image, 1, 0, cv::Mat(), hist, 1, &histSize, &histRange);

    // Normalize histogram
    hist /= image.total();

    // Calculate entropy
    double entropy = 0;
    for (int i = 0; i < histSize; ++i)
    {
        if (hist.at<float>(i) > 0)
        {
            entropy -= hist.at<float>(i) * std::log2(hist.at<float>(i));
        }
    }
    return entropy;
}

void RLEnvironment::CalculateImageFeatures()
{
    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexImagePixel.try_lock_for(std::chrono::milliseconds(1))) {
        // Try to acquire the timed_mutex with a timeout of 1 milliseconds
        if (mMutexImageFeatures.try_lock_for(std::chrono::milliseconds(1))) {
            if (mbImageFeaturesReady)
            {
                if (mImGrey.empty())
                {
                    cout << "Failed to load image." << endl;
                }
                else {
                    cv::resize(mImGrey, mImGrey, cv::Size(), 0.5, 0.5, cv::INTER_NEAREST);
                    cv::Scalar meanValue, stddevValue;
                    // calculate the brightness and contrast
                    cv::meanStdDev(mImGrey, meanValue, stddevValue);
                    mdBrightness = meanValue[0];
                    mdContrast = stddevValue[0];
                    // calculate the entropy
                    mdEntropy = CalculateImageEntropy(mImGrey);

                    cv::Mat laplacianImage;
                    cv::Laplacian(mImGrey, laplacianImage, CV_16S, 3);
                    // Since the radius of ORB feature extractor is 16?? Sorry must be odd number
                    cv::Laplacian(mImGrey, laplacianImage, CV_16S, 5);
                    cv::convertScaleAbs(laplacianImage, laplacianImage);
                    //cv::imshow("laplacian", laplacianImage);
                    //cv::waitKey(1);
                    cv::meanStdDev(laplacianImage, meanValue, stddevValue);
                    mdLaplacian = stddevValue[0]; //meanValue[0];
                }
            }
            mMutexImageFeatures.unlock();
        }
        else {
            std::cout << " failed to acquire the mMutexImageFeatures within 1 milliseconds." << std::endl;
        }
        mMutexImagePixel.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexImagePixel within 1 milliseconds." << std::endl;
    }
}


void RLEnvironment::CollectCurrentFrameNumberKeyPoint(int nKeyPoint)
{
    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexCurrentFrameNumberKeyPoint.try_lock_for(std::chrono::milliseconds(1))) {
        mnKeyPoint = nKeyPoint;
        mMutexCurrentFrameNumberKeyPoint.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexCurrentFrameNumberKeyPoint within 1 milliseconds." << std::endl;
    }
}


void RLEnvironment::CollectCurrentFramePose(Sophus::SE3f currentTwc)
{
    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexCurrentFramePose.try_lock_for(std::chrono::milliseconds(1))) {
        // get current pose
        // 0current camera pose in world reference
        // Sophus::SE3f currentTwc = mCurrentFrame.GetPose().inverse();
        mQ = currentTwc.unit_quaternion();
        mtwc = currentTwc.translation();
        // calculate relative pose
        Sophus::SE3f currentRelativePose = mTwc.inverse() * currentTwc;
        Eigen::Matrix3f rotationMatrix = currentRelativePose.rotationMatrix();
        mREuler = rotationMatrix.eulerAngles(2, 1, 0); // ZYX convention
        mRtwc = currentRelativePose.translation();
        // update current camera pose
        mTwc = currentTwc;
        mMutexCurrentFramePose.unlock();
    }
    else {
        std::cout << " failed to acquire the mMutexCurrentFramePose within 1 milliseconds." << std::endl;
    }
}

void RLEnvironment::CollectCurrentNumberKeyFrame(int keyFrameinMap){
    // Try to acquire the timed_mutex with a timeout of 1 milliseconds
    if (mMutexCurrentNumberKeyFrame.try_lock_for(std::chrono::milliseconds(1))) {
        mnKeyFrame = keyFrameinMap;
        mMutexCurrentNumberKeyFrame.unlock();
    }
    else {
    std::cout << " failed to acquire the mMutexCurrentNumberKeyFrame within 1 milliseconds." << std::endl;
}

}

void RLEnvironment::InitializeCSVLogger()
{
    msCSVFileName = "./logs/log.csv";

    // Open the CSV file for writing
    mFileLogger.open(msCSVFileName);

    // Write the first row with column names
    if (!mFileLogger.is_open())
    {
        std::cerr << "Unable to open file: " << msCSVFileName << std::endl;
    }
    else
    {
        size_t totalSize = mvsColumnFeatureNames.size();
        for (size_t i = 0; i < totalSize; ++i) {
            const auto& columnName = mvsColumnFeatureNames[i];
            if (i < totalSize-1){
                mFileLogger << columnName << ",";
            }
            else{
                mFileLogger << columnName;
            }
        }
        mFileLogger << endl;
    }
}


void RLEnvironment::InitializeTCPClient(const std::string& serverIP, int serverPort) {
    // Create a socket
    mpTCPClient = new TCPClient(serverIP, serverPort);
    mpTCPClient->Connect();
}


void RLEnvironment::WriteRowCSVLogger()
{
    if (!mFileLogger.is_open())
    {
        std::cerr << "Unable to open file: " << msCSVFileName << std::endl;
    }
    else
    {
        // Try to acquire the timed_mutex with a timeout of 10 milliseconds
        if (mMutexImageTimeStamp.try_lock_for(std::chrono::milliseconds(10))) {
            mFileLogger << fixed << setprecision(6) << mdTimeStamp << ","; //1e9*mdTimeStamp << ",";
            mMutexImageTimeStamp.unlock();
        }
        else {
            std::cout << " failed to acquire the mMutexImageTimeStamp in CSV logger within 10 milliseconds." << std::endl;
            return;
        }

        // Try to acquire the timed_mutex with a timeout of 10 milliseconds
        if (mMutexCurrentFrameTrackMode.try_lock_for(std::chrono::milliseconds(10))) {
            mFileLogger << mnTrackMode << ",";
            mMutexCurrentFrameTrackMode.unlock();
        }
        else {
            std::cout << " failed to acquire the mMutexCurrentFrameTrackMode in CSV logger within 10 milliseconds." << std::endl;
            return;
        }

        if(mbImageFeaturesReady)
        {
            // Try to acquire the timed_mutex with a timeout of 10 milliseconds
            if (mMutexImageFeatures.try_lock_for(std::chrono::milliseconds(10))) {
                mFileLogger << fixed << std::setprecision(6);
                mFileLogger << mdBrightness << "," << mdContrast << "," << mdEntropy << "," << mdLaplacian << ",";

                mMutexImageFeatures.unlock();
            }
            else {
                std::cout << " failed to acquire the mMutexImageFeatures in CSV logger within 10 milliseconds." << std::endl;
                return;
            }
        }
        else
        {
            mFileLogger << ","  << ","  << ","  << ",";
        }

        if(mbCurrentFrameFeaturesReady)
        {
            // Try to acquire the timed_mutex with a timeout of 10 milliseconds
            if (mMutexCurrentFrameMatchedInlier.try_lock_for(std::chrono::milliseconds(10))) {
                mFileLogger << mnMatchedInlier << ",";
                mMutexCurrentFrameMatchedInlier.unlock();
            }
            else {
                std::cout << " failed to acquire the mMutexCurrentFrameMatchedInlier in CSV logger within 10 milliseconds." << std::endl;
                return;
            }

            // Try to acquire the timed_mutex with a timeout of 10 milliseconds
            if (mMutexCurrentFrameFeatures.try_lock_for(std::chrono::milliseconds(10))) {
                mFileLogger << mnKeyPoint << "," << mnKeyFrame << ",";
                mFileLogger << setprecision(9) << mtwc(0) << "," << mtwc(1) << "," << mtwc(2) << ",";
                mFileLogger << mQ.x() << "," << mQ.y() << "," << mQ.z() << "," << mQ.w() << ",";
                mFileLogger << mRtwc(0) << "," << mRtwc(1) << "," << mRtwc(2) << ",";
                mFileLogger << mREuler(0) << "," << mREuler(1) << "," << mREuler(2) << ",";
                mMutexCurrentFrameFeatures.unlock();
            }
            else {
                std::cout << " failed to acquire the mMutexCurrentFrameFeatures in CSV logger within 10 milliseconds." << std::endl;
                return;
            }


        }
        else
        {
            mFileLogger << ","  << "," << ","  << ","  << "," << ","  << ","  << ","  << "," << ","  << ","  << ","  << "," << ","  << ","  << ",";
        }
        mFileLogger << mfActionThRefRatio << "," << mnActionMinFrames << "," << mnActionMaxFrames;

        mFileLogger << endl;
    }
}


void RLEnvironment::SendRowTCP()
{
    if (!mpTCPClient)
    {
        std::cerr << "TCP port haven't initialized" << std::endl;
    }
    else
    {
        std::ostringstream csvRow;

        // Try to acquire the timed_mutex with a timeout of 10 milliseconds
        if (mMutexImageTimeStamp.try_lock_for(std::chrono::milliseconds(10))) {
            csvRow << fixed << setprecision(6) << mdTimeStamp << ","; //1e9*mdTimeStamp << ",";
            mMutexImageTimeStamp.unlock();
        }
        else {
            std::cout << " failed to acquire the mMutexImageTimeStamp in CSV logger within 10 milliseconds." << std::endl;
            return;
        }

        // Try to acquire the timed_mutex with a timeout of 10 milliseconds
        if (mMutexCurrentFrameTrackMode.try_lock_for(std::chrono::milliseconds(10))) {
            csvRow << mnTrackMode << ",";
            mMutexCurrentFrameTrackMode.unlock();
        }
        else {
            std::cout << " failed to acquire the mMutexCurrentFrameTrackMode in CSV logger within 10 milliseconds." << std::endl;
            return;
        }

        if(mbImageFeaturesReady)
        {
            // Try to acquire the timed_mutex with a timeout of 10 milliseconds
            if (mMutexImageFeatures.try_lock_for(std::chrono::milliseconds(10))) {
                csvRow << fixed << std::setprecision(6);
                csvRow << mdBrightness << "," << mdContrast << "," << mdEntropy << "," << mdLaplacian << ",";

                mMutexImageFeatures.unlock();
            }
            else {
                std::cout << " failed to acquire the mMutexImageFeatures in CSV logger within 10 milliseconds." << std::endl;
                return;
            }
        }
        else
        {
            csvRow << ","  << ","  << ","  << ",";
        }

        if(mbCurrentFrameFeaturesReady)
        {
            // Try to acquire the timed_mutex with a timeout of 10 milliseconds
            if (mMutexCurrentFrameMatchedInlier.try_lock_for(std::chrono::milliseconds(10))) {
                csvRow << mnMatchedInlier << ",";
                mMutexCurrentFrameMatchedInlier.unlock();
            }
            else {
                std::cout << " failed to acquire the mMutexCurrentFrameMatchedInlier in CSV logger within 10 milliseconds." << std::endl;
                return;
            }
            // Try to acquire the timed_mutex with a timeout of 10 milliseconds
            if (mMutexCurrentFrameFeatures.try_lock_for(std::chrono::milliseconds(10))) {
                csvRow << mnKeyPoint << "," << mnKeyFrame << ",";
                csvRow << setprecision(9) << mtwc(0) << "," << mtwc(1) << "," << mtwc(2) << ",";
                csvRow << mQ.x() << "," << mQ.y() << "," << mQ.z() << "," << mQ.w() << ",";
                csvRow << mRtwc(0) << "," << mRtwc(1) << "," << mRtwc(2) << ",";
                csvRow << mREuler(0) << "," << mREuler(1) << "," << mREuler(2);
                mMutexCurrentFrameFeatures.unlock();
            }
            else {
                std::cout << " failed to acquire the mMutexCurrentFrameFeatures in CSV logger within 10 milliseconds." << std::endl;
                return;
            }
        }
        else
        {
            csvRow << ","  << ","  << "," << "," << "," << ","  << ","  << ","  << "," << ","  << ","  << ","  << "," << ","  << ",";
        }
        //csvRow << mfActionThRefRatio << "," << mnActionMinFrames << "," << mnActionMaxFrames;

        std::string csvString = csvRow.str();
        mpTCPClient->SendMessage(csvString);
    }
}

void RLEnvironment::SetTCP2Actions()
{
    std::string receivedMessage;
    if (mpTCPClient->ReceiveMessage(receivedMessage)) {
        std::vector<float> floats;

        std::istringstream ss(receivedMessage);
        std::string token;

        while (std::getline(ss, token, ',')) {
            try {
                float value = std::stof(token);
                floats.push_back(value);
            } catch (const std::invalid_argument& e) {
                // Handle invalid float value
                std::cerr << "Invalid float value: " << token << std::endl;
            }
        }
//        std::cout << "Receive actions: ";
//        for (float f : floats) {
//            std::cout << setprecision(3) << f << " ";
//        }
//
//        std::cout << std::endl;

        mfActionThRefRatio = floats[0];
        mnActionMinFrames = (int)floats[1];
        mnActionMaxFrames = (int)floats[2];
    }
}

float RLEnvironment::GetActionThRefRatio()
{
    return mfActionThRefRatio;
}

int RLEnvironment::GetActionMaxFrames()
{
    return mnActionMaxFrames;
}

int RLEnvironment::GetActionMinFrames()
{
    return mnActionMinFrames;
}


// End of the namespace
}
