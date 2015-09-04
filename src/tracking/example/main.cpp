#include <stdio.h>
#include <iostream>
#include <vector>
#include <iomanip>
#include <string>

#include <OpenNI.h>
#include <opencv2/opencv.hpp>

#define MIN_HIGH 100
#define MAX_HIGH 10000
#define MIN_AREA 1000

cv::Mat morphology(cv::Mat frame);

int main(int argc, char* argv[])
{
    try {
        openni::OpenNI::initialize();
        openni::Device device;

        const char* deviceURI = openni::ANY_DEVICE;
        if (argc > 1) {
            deviceURI = argv[1];
        }

        auto ret = device.open(deviceURI);


        if (ret != openni::STATUS_OK) {
            throw std::runtime_error("can't open device");
        }

        auto playbackControl = device.getPlaybackControl();
        playbackControl->setRepeatEnabled(false);

        openni::VideoStream colorStream;
        colorStream.create(device, openni::SensorType::SENSOR_COLOR);
        colorStream.start();

        openni::VideoStream depthStream;
        depthStream.create(device, openni::SensorType::SENSOR_DEPTH);
        depthStream.start();

        openni::VideoFrameRef depthFrame;
        openni::VideoFrameRef colorFrame;

        cv::Mat colorImage;
        cv::Mat depthImage;
        cv::Mat depthImageBack;
        cv::Mat depthImageFore;
        cv::Mat depthoutputImage;
        cv::Mat maskImage;
        cv::Mat zeroMaskBack;

        std::string videoID(device.getDeviceInfo().getUri());

        videoID.erase(videoID.begin(), videoID.end() - 7);
        videoID.erase(videoID.begin() + 3, videoID.end());

        std::string pathBase(device.getDeviceInfo().getUri());
        pathBase.erase(pathBase.end() - 11, pathBase.end());

        auto idPerson = std::atoi(videoID.c_str());

        auto oldNoFrame = 0;
        auto NoFrame = 1;

        do {
            // depth frame
            depthStream.readFrame(&depthFrame);
            if (depthFrame.isValid()) {
                depthImage = cv::Mat(depthFrame.getVideoMode().getResolutionY(),
                                     depthFrame.getVideoMode().getResolutionX(),
                                     CV_16UC1, (unsigned short*)depthFrame.getData());

                depthImage.convertTo(depthoutputImage, CV_8UC1, 255.0/10000);
                cv::cvtColor(depthoutputImage, depthoutputImage, CV_GRAY2BGR);
            }

            // color frame
            colorStream.readFrame(&colorFrame);
            if (colorFrame.isValid()) {
                colorImage = cv::Mat(colorStream.getVideoMode().getResolutionY(),
                                     colorStream.getVideoMode().getResolutionX(),
                                     CV_8UC3, (char*)colorFrame.getData());
                cv::cvtColor(colorImage, colorImage, CV_RGB2BGR);
            }

            // process
            if (NoFrame == 1) {
                depthImageBack = depthImage.clone();
                depthImageFore = cv::Mat::zeros(depthImage.rows,depthImage.cols, CV_16UC1);
                zeroMaskBack = depthImageBack == 0;
                std::cout << videoID <<";NULL;NULL;NULL;NULL;"
                          << depthFrame.getTimestamp() << ";" << depthFrame.getFrameIndex() << ";"
                          << colorFrame.getTimestamp() << ";" << colorFrame.getFrameIndex() << std::endl;

                std::string pathImgBack;
                pathImgBack = pathBase + "img/background.png";
                cv::imwrite(pathImgBack, colorImage);
                pathImgBack = pathBase + "depth/background.png";
                cv::imwrite(pathImgBack, depthImage);

            } else {
                depthImageFore = depthImageBack - depthImage;
                maskImage = depthImageFore > MIN_HIGH & depthImageFore < MAX_HIGH;

                // morfology
                maskImage = morphology(maskImage);

                // find contours
                std::vector<std::vector<cv::Point> > contours;
                cv::findContours(maskImage.clone(), contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);

                auto noPerson = 0;

                for (auto c_iter = contours.begin(); c_iter != contours.end(); ++c_iter) {
                    auto area = cv::contourArea(*c_iter);
                    // filtering by area
                    if (area > (MIN_AREA)) {
                        noPerson++;
                    } else {
                        // clean vector of contours
                        contours.erase(c_iter--);
                    }
                }

                if (contours.size()) {
                    oldNoFrame = NoFrame;
                    // Draw contours
                    cv::Mat drawing = cv::Mat::zeros(maskImage.size(), CV_8UC1);
                    for(auto i = 0; i < contours.size(); ++i)
                    {
                        cv::drawContours(drawing, contours, i, 255, -1);
                    }

                    cv::Mat zeroMask = depthImage == 0;
                    cv::Mat zeroMaskTot;
                    cv::bitwise_or(zeroMask, zeroMaskBack, zeroMaskTot);
                    drawing = drawing - zeroMaskTot;

                    cv::Mat depthImageFilter;
                    depthImageFore.copyTo(depthImageFilter, drawing);

                    // cv::imshow("depthImageFilter", depthImageFilter);
                    // cv::imshow("drawing", drawing);

                    if (NoFrame % 10 == 0) {
                        std::string pathImgColor;
                        pathImgColor = pathBase + "img/" + std::to_string(depthFrame.getFrameIndex()) + ".png";
                        cv::imwrite(pathImgColor, colorImage);

                        std::string pathImgDepth;
                        pathImgDepth = pathBase + "depth/" + std::to_string(depthFrame.getFrameIndex()) + ".png";
                        cv::imwrite(pathImgDepth, depthImage);

                        std::string pathImgMask;
                        pathImgMask = pathBase + "mask/" + std::to_string(depthFrame.getFrameIndex()) + ".png";
                        cv::imwrite(pathImgMask, drawing);
                    }

                    double maxValue;
                    cv::Point maxPoint;

                    cv::minMaxLoc(depthImageFilter, NULL, &maxValue, NULL, &maxPoint);

                    maxValue += int(depthImageBack.at<unsigned short>(cv::Point(depthImageBack.cols/2-1, depthImageBack.rows/2-1))) - depthImageBack.at<unsigned short>(maxPoint);

                    std::cout << videoID  << ";" << std::setfill('0') << std::setw(3) << idPerson << ";"
                              << maxValue << ";"
                              << maxPoint.x << ";"
                              << maxPoint.y << ";"
                              << depthFrame.getTimestamp() << ";" << depthFrame.getFrameIndex() << ";"
                              << colorFrame.getTimestamp() << ";" << colorFrame.getFrameIndex() << std::endl;
                    // cv::circle(colorImage, maxPoint, 5, cv::Scalar(255, 50, 0), -1, 8, 0);
                } else {
                    if (!(oldNoFrame - NoFrame + 1)) {
                        ++idPerson;
                    }
                    std::cout << videoID <<";NULL;NULL;NULL;NULL;"
                              << depthFrame.getTimestamp() << ";" << depthFrame.getFrameIndex() << ";"
                              << colorFrame.getTimestamp() << ";" << colorFrame.getFrameIndex() << std::endl;
                }
            }
            // cv::imshow("Color Camera", colorImage);
            // cv::imshow("Depth CameraFore", depthImageFore);

            int key = cv::waitKey(10);
            if (key == 'q') {
                break;
            }

            ++NoFrame;
        } while (depthFrame.getFrameIndex() < playbackControl->getNumberOfFrames(depthStream) && colorFrame.getFrameIndex() < playbackControl->getNumberOfFrames(colorStream));

        depthStream.destroy();
        colorStream.destroy();
        device.close();

        openni::OpenNI::shutdown();
        return 0;
    }
    catch ( std::exception& ) {
        std::cout << openni::OpenNI::getExtendedError() << std::endl;
    }
}

cv::Mat morphology(cv::Mat frame)
{
    cv::Mat process;
    int size_slider = 3;
    cv::Mat st_elem = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(size_slider, size_slider));
    cv::dilate(frame, process, 3);
    cv::erode(process, process, st_elem);
    cv::erode(process, process, st_elem);
    cv::dilate(process, process, 2);
    return process;
}
