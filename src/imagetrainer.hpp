//
// Created by Michael Stevens on 3/15/23.
//

#ifndef __IMAGETRAINER_HPP__
#define __IMAGETRAINER_HPP__

#include <string>

#include "environment.hpp"
#include "main.hpp"

/**
 * A simple supervised "image label" training environment.
 * Observation is a class id in [0, classes-1].
 * Action is an agent's predicted class id. Reward is 1 on match, else 0.
 *
 * Options (optional):
 * - image-classes: number of classes (default 4)
 * - image-max-steps: max steps before isFinished() (default 0 = never)
 */
class ImageTrainer : public Environment {
public:
    explicit ImageTrainer(options_t &options);

    void performAction(action_t action) override;
    bool isFinished(void) const override;

    action_t maxAction() const override;
    percept_t maxObservation() const override;
    percept_t maxReward() const override;

    std::string print(void) const override;

private:
    int m_classes;      // number of label classes
    int m_max_steps;    // 0 for infinite
    int m_steps;        // steps taken
};

#endif // __IMAGETRAINER_HPP__
