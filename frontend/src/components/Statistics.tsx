import { useEffect, useState } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { ResponsivePie } from '@nivo/pie';
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';

interface StatisticsData {
    matches_per_day: Record<string, number>;
    average_user_score: Record<string, number>;
    ai_performance: Record<string, { matches_played: number }>;
}

const Statistics = () => {
    const [data, setData] = useState<StatisticsData | null>(null);
    const kinde_uuid = useKindeAuth().user?.id;

    useEffect(() => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/statistics`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'kinde_uuid': kinde_uuid || '',
            },
        })
            .then(response => response.json())
            .then(data => setData(data as StatisticsData));
    }, [kinde_uuid]);

    if (!data) return <div>Loading...</div>;

    const matchesPerDayData = Object.keys(data.matches_per_day).map(date => ({
        x: date,
        y: data.matches_per_day[date]
    }));

    const averageUserScoreData = Object.keys(data.average_user_score).map(date => ({
        x: date,
        y: data.average_user_score[date]
    }));

    const aiPerformanceData = Object.keys(data.ai_performance).map(aiType => ({
        id: aiType,
        label: aiType,
        value: data.ai_performance[aiType].matches_played
    }));

    return (
        <div>
            <h2>Matches Per Day</h2>
            <div style={{ height: 400 }}>
                <ResponsiveLine
                    data={[{ id: 'matches', data: matchesPerDayData }]}
                    margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
                    xScale={{ type: 'point' }}
                    yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: true, reverse: false }}
                    axisTop={null}
                    axisRight={null}
                    axisBottom={{
                        legend: 'Date',
                        legendOffset: 36,
                        legendPosition: 'middle'
                    }}
                    axisLeft={{
                        legend: 'Matches',
                        legendOffset: -40,
                        legendPosition: 'middle'
                    }}
                />
            </div>

            <h2>Average User Score Over Past Month</h2>
            <div style={{ height: 400 }}>
                <ResponsiveLine
                    data={[{ id: 'average_score', data: averageUserScoreData }]}
                    margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
                    xScale={{ type: 'point' }}
                    yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: true, reverse: false }}
                    axisTop={null}
                    axisRight={null}
                    axisBottom={{
                        legend: 'Date',
                        legendOffset: 36,
                        legendPosition: 'middle'
                    }}
                    axisLeft={{
                        legend: 'Average Score',
                        legendOffset: -40,
                        legendPosition: 'middle'
                    }}
                />
            </div>

            <h2>AI Performance</h2>
            <div style={{ height: 400 }}>
                <ResponsivePie
                    data={aiPerformanceData}
                    margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
                    innerRadius={0.5}
                    padAngle={0.7}
                    cornerRadius={3}
                    activeOuterRadiusOffset={8}
                    borderWidth={1}
                    borderColor={{ from: 'color', modifiers: [['darker', 0.2]] }}
                    arcLinkLabelsSkipAngle={10}
                    arcLinkLabelsTextColor="#333333"
                    arcLinkLabelsThickness={2}
                    arcLinkLabelsColor={{ from: 'color' }}
                    arcLabelsSkipAngle={10}
                    arcLabelsTextColor={{ from: 'color', modifiers: [['darker', 2]] }}
                />
            </div>
        </div>
    );
};

export default Statistics;
