"""
Project Palantír
================

File:
    army.py

Purpose:
    Defines the Army class for MESBG army lists.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-006 – Army Class
"""

from profiles import Profile
from army_entry import ArmyEntry
from metrics import AnalysisMetrics
from analysis import ArmyAnalysis


class Army:
    """
    Represents a single MESBG army.
    """

    def __init__(self):
        """
        Creates an empty army.
        """

        self.entries = []

    def add_profile(self, profile: Profile, quantity: int = 1) -> None:
        """
        Adds a profile to the army.

        Args:
            profile:
                The Profile to add.
        """
        entry = ArmyEntry(profile=profile, quantity=quantity,)
        self.entries.append(entry)

    def _total_attribute(self, attribute: str) -> int:
        """
        Returns the total of a chosen attribute across the army.
        """

        total = 0

        for entry in self.entries:
            total += entry.total_attribute(attribute)

        return total 

    def _highest_profile(self, attribute: str) -> Profile:
        """
        Returns the profile with the highest value of a chosen attribute.
        """

        highest_entry = self.entries[0]

        for entry in self.entries:

            if (
                entry.get_attribute(attribute)
                >
                highest_entry.get_attribute(attribute)
            ):
                highest_entry = entry

        return highest_entry.profile

    def _lowest_profile(self, attribute: str) -> Profile:
        """
        Returns the profile with the lowest value of a chosen attribute.
        """

        lowest_entry = self.entries[0]

        for entry in self.entries:

            profile = entry.profile

            if (
                entry.get_attribute(attribute)
            <    lowest_entry.get_attribute(attribute)
            ):
                lowest_entry = entry

        return lowest_entry.profile     

    
    def total_points(self) -> int:
        """
        Returns the total points value of the army.
        """

        return self._total_attribute("points") 
    
    def total_might(self) -> int:
        """
        Returns the total Might in the army.
        """

        return self._total_attribute("might")
    
    def total_will(self) -> int:
        """
        Returns the total Will in the army.
        """

        return self._total_attribute("will")
    
    def total_fate(self) -> int:
        """
        Returns the total Fate in the army.
        """

        return self._total_attribute("fate")
    
    def highest_fight(self) -> Profile:
        """
        Returns the profile with the highest Fight value.
        """

        return self._highest_profile("fight")
    
    def highest_strength(self) -> Profile:
        """
        Returns the profile with the highest Strength value.
        """

        return self._highest_profile("strength")
    
    def highest_defence(self) -> Profile:
        """
        Returns the profile with the highest Defence value.
        """

        return self._highest_profile("defence")
    
    def lowest_fight(self) -> Profile:
        """
        Returns the profile with the lowest Fight value.
        """

        return self._lowest_profile("fight")
    
    def lowest_strength(self) -> Profile:
        """
        Returns the profile with the lowest Strength value.
        """

        return self._lowest_profile("strength")
    
    def lowest_defence(self) -> Profile:
        """
        Returns the profile with the lowest Defence value.
        """

        return self._lowest_profile("defence")

    def profile_count(self) -> int:
        """
        Returns the number of profiles in the army

        """
        return len(self.entries) 
    
    def analysis_metrics(self) -> AnalysisMetrics:
        """
        Returns calculated metrics describing the army.
        """
        return AnalysisMetrics(

        might_density=(
            self.total_might()
            / self.total_points()
            * 100
        ),

        will_density=(
            self.total_will()
            / self.total_points()
            * 100
        ),

        fate_density=(
            self.total_fate()
            / self.total_points()
            * 100
        ),

        profile_density=(
            self.profile_count()
            / self.total_points()
            * 100
        ),

        model_count=self.model_count(),

        model_density=(
            self.model_count()
            / self.total_points()
            * 100
        ),
    
        average_movement=self.average_movement(),

        fast_model_density=(
            self.fast_model_count()
            / self.total_points()
            * 100
        ),

        standard_model_density=(
            self.standard_model_count()
            / self.total_points()
            * 100
        ),

        slow_model_density=(
            self.slow_model_count()
            / self.total_points()
            * 100
        ),

        average_fight=self.average_fight(),

        average_strength=self.average_strength(),

        average_attacks=self.average_attacks(),

        high_fight_density=(
            self.high_fight_model_count()
            / self.total_points()
            * 100
        ),

        high_strength_density=(
            self.high_strength_model_count()
            / self.total_points()
            * 100
        ),

        average_defence=self.average_defence(),

        average_wounds=self.average_wounds(),

        high_defence_density=(
            self.high_defence_model_count()
            / self.total_points()
            * 100
        ),

        multi_wound_density=(
            self.multi_wound_model_count()
            / self.total_points()
            * 100
        ),

    )

    

    def analyse(self) -> ArmyAnalysis:
        """
        Analyses the army and returns an ArmyAnalysis.
        """

        metrics = self.analysis_metrics()

        analysis = ArmyAnalysis()

        self._analyse_might(
            metrics,
            analysis,
        )

        self._analyse_will(
            metrics,
            analysis,
        )

        self._analyse_fate(
        metrics,
        analysis,
        )

        return analysis
    
    def _analyse_might(
        self,
        metrics: AnalysisMetrics,
            analysis: ArmyAnalysis,
    ) -> None:
        """
        Analyses the army's Heroic Resources.
        """
        if metrics.might_density >= 1.5:

            analysis.strengths.append(
            f"Exceptional Heroic Resources. "
            f"(Might Density: {metrics.might_density:.2f})"
        )
        
        elif metrics.might_density <= 0.5:

            analysis.weaknesses.append(
            f"Limited Heroic Resources. "
            f"(Might Density: {metrics.might_density:.2f})"
        )
    
    def _analyse_will(
        self,
        metrics: AnalysisMetrics,
        analysis: ArmyAnalysis,
    ) -> None:
        """
        Analyses the army's Magical Resources.
        """

        if metrics.will_density >= 2.0:

            analysis.strengths.append(
                f"Exceptional Magical Resources. "
                f"(Will Density: {metrics.will_density:.2f})"
            )

        elif metrics.will_density >= 1.2:

            analysis.strengths.append(
                f"Strong Magical Resources. "
                f"(Will Density: {metrics.will_density:.2f})"
            )

        elif metrics.will_density <= 0.4:

            analysis.weaknesses.append(
                f"Limited Magical Resources. "
                f"(Will Density: {metrics.will_density:.2f})"
            )

    def _analyse_fate(
        self,
        metrics: AnalysisMetrics,
        analysis: ArmyAnalysis,
    ) -> None:
        """
        Analyses the army's Heroic Resilience.
        """

        if metrics.fate_density >= 1.0:

            analysis.strengths.append(
                f"High Heroic Resilience. "
                f"(Fate Density: {metrics.fate_density:.2f})"
            )

        elif metrics.fate_density <= 0.2:

            analysis.weaknesses.append(
                f"Limited Heroic Resilience. "
                f"(Fate Density: {metrics.fate_density:.2f})"
            )
    def validate(self, points_limit: int,) -> list[str]:
        """
        Validates the army.

        Returns:
             A list of validation errors.
            An empty list means the army is valid.
        """

        errors = []

        errors.extend(
            self._validate_max_in_army()
        )

        errors.extend(
            self._validate_points_limit(points_limit)
        )

        return errors
    
    def _validate_max_in_army(self) -> list[str]:
        """
        Validates that no profile exceeds its
        maximum permitted quantity.
        """

        errors = []

        for entry in self.entries:

            max_allowed = entry.profile.max_in_army

            if max_allowed == 0:
                continue

            if entry.quantity > max_allowed:

                errors.append(
                    f"{entry.profile.name} "
                    f"may only be taken "
                    f"{max_allowed} time(s)."
                )

        return errors
    
    def _validate_points_limit(self, points_limit: int,) -> list[str]:
        """
        Validates that the army does not exceed
        the agreed points limit.
        """

        errors = []

        if self.total_points() > points_limit:

            errors.append(
                f"Army is {self.total_points()} points "
                f"(limit: {points_limit})."
            )

        return errors

    def model_count(self) -> int:
        """
        Returns the total number of models in the army.
        """ 
        total = 0

        for entry in self.entries:
            total += entry.quantity

        return total
    
    def _count_models(
            self,
        predicate,
        ) -> int:
        """
        Counts models matching a supplied condition.

        Args:
            predicate:
                Function accepting a Profile and returning True
                if the model should be counted.

        Returns:
            Total number of matching models.
        """

        total = 0

        for entry in self.entries:

            if predicate(entry.profile):

                total += entry.quantity

        return total
    
    def _average_profile_stat(
            self,
        selector,
        ) -> float:
        """
        Returns the quantity-weighted average of a profile statistic.

        Args:
            selector:
                Function accepting a Profile and returning the
                statistic to average.

        Returns:
            Quantity-weighted average value.
        """

        total = 0

        for entry in self.entries:

            total += (
                selector(entry.profile)
                * entry.quantity
            )

        return (
            total
            / self.model_count()
        )

    def fast_model_count(self) -> int:
        """
        Returns the number of fast models.
        """

        return self._count_models(
            lambda profile: profile.movement >= 8
        )

    def standard_model_count(self) -> int:
        """
        Returns the number of standard movement models.
        """

        return self._count_models(
            lambda profile: profile.movement == 6
        )

    def slow_model_count(self) -> int:
        """
        Returns the number of slow models.
        """

        return self._count_models(
            lambda profile: profile.movement <= 5
        )

    def average_movement(self) -> float:
        """
        Returns the army's quantity-weighted average movement.
        """

        return self._average_profile_stat(
            lambda profile: profile.movement
        )
    
    def average_fight(self) -> float:
        """
        Returns the army's quantity-weighted average Fight value.
        """

        return self._average_profile_stat(
            lambda profile: profile.fight
        )
    
    def average_strength(self) -> float:
        """
        Returns the army's quantity-weighted average Strength value.
        """

        return self._average_profile_stat(
            lambda profile: profile.strength
        )
    
    def average_attacks(self) -> float:
        """
        Returns the army's quantity-weighted average Attacks value.
        """

        return self._average_profile_stat(
            lambda profile: profile.attacks
        )
    
    def average_defence(self) -> float:
        """
        Returns the army's quantity-weighted average Defence value.
        """

        return self._average_profile_stat(
            lambda profile: profile.defence
        )

    def average_wounds(self) -> float:
        """
        Returns the army's quantity-weighted average Wounds value.
        """

        return self._average_profile_stat(
            lambda profile: profile.wounds
        )

    def high_fight_model_count(self) -> int:
        """
        Returns the number of models with Fight 5 or higher.
        """

        return self._count_models(
            lambda profile: profile.fight >= 5
        )   
    
    def high_strength_model_count(self) -> int:
        """
        Returns the number of models with Strength 5 or higher.
        """

        return self._count_models(
            lambda profile: profile.strength >= 5
        )
    
    def high_defence_model_count(self) -> int:
        """
        Returns the number of models with Defence 6 or higher.
        """

        return self._count_models(
            lambda profile: profile.defence >= 6
        )
    
    def multi_wound_model_count(self) -> int:
        """
        Returns the number of models with 2 or more Wounds.
        """

        return self._count_models(
            lambda profile: profile.wounds >= 2
        )