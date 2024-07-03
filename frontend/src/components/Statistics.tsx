import { useEffect, useState } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { ResponsivePie } from '@nivo/pie';
import { ResponsiveBar } from '@nivo/bar';
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import Loading from './partials/Loading';

interface StatisticsData {
    matches_per_day: Record<string, number>;
    average_user_score: Record<string, number>;
    ai_performance: Record<string, { matches_played: number }>;
    user_win_rates: Record<string, { user_name: string, win_rate: number }>;
    ai_win_rates: Record<string, { win_rate: number }>;
    score_distribution: { user_score: number; ai_score: number }[];
    player_activity: Record<string, number>;
}

const getDayOfWeek = (dateStr: string) => {
    const date = new Date(dateStr);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getUTCDay()];
};

const MyResponsiveBar = ({ data, keys, indexBy, xLegend, yLegend } : {
    data: { day: string, matches: number }[],
    keys: string[],
    indexBy: string,
    xLegend: string,
    yLegend: string
}) => {
    console.log('Bar chart data:', data); // Log the data being passed to the component
    return (
        <ResponsiveBar
            data={data}
            keys={keys}
            indexBy={indexBy}
            margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
            padding={0.3}
            valueScale={{ type: 'linear' }}
            indexScale={{ type: 'band', round: true }}
            colors={{ scheme: 'pink_yellowGreen'}}
            groupMode='grouped'
            borderColor={{
                from: 'color',
                modifiers: [
                    ['darker', 1.6]
                ]
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: xLegend,
                legendPosition: 'middle',
                legendOffset: 32
            }}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: yLegend,
                legendPosition: 'middle',
                legendOffset: -40
            }}
            labelSkipWidth={12}
            labelSkipHeight={12}
            labelTextColor={{
                from: 'color',
                modifiers: [
                    ['darker', 1.6]
                ]
            }}
            legends={[
                {
                    dataFrom: 'keys',
                    anchor: 'bottom-right',
                    direction: 'column',
                    justify: false,
                    translateX: 120,
                    translateY: 0,
                    itemsSpacing: 2,
                    itemWidth: 100,
                    itemHeight: 20,
                    itemDirection: 'left-to-right',
                    itemOpacity: 0.85,
                    symbolSize: 20,
                    effects: [
                        {
                            on: 'hover',
                            style: {
                                itemOpacity: 1
                            }
                        }
                    ]
                }
            ]}
            role="application"
            ariaLabel="Nivo bar chart"
            barAriaLabel={e => e.id + ": " + e.formattedValue + " on " + indexBy + ": " + e.indexValue}
        />
    );
};

const MyResponsiveBarAverageScore = ({ data, keys, indexBy, xLegend, yLegend } : {
    data: { date: string, averageScore: number }[],
    keys: string[],
    indexBy: string,
    xLegend: string,
    yLegend: string
}) => {
    console.log('Bar chart data:', data); // Log the data being passed to the component
    return (
        <ResponsiveBar
            data={data}
            keys={keys}
            indexBy={indexBy}
            margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
            padding={0.3}
            valueScale={{ type: 'linear' }}
            indexScale={{ type: 'band', round: true }}
            colors={{ scheme: 'pink_yellowGreen'}}
            groupMode='grouped'
            borderColor={{
                from: 'color',
                modifiers: [
                    ['darker', 1.6]
                ]
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: xLegend,
                legendPosition: 'middle',
                legendOffset: 32
            }}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: yLegend,
                legendPosition: 'middle',
                legendOffset: -40
            }}
            labelSkipWidth={12}
            labelSkipHeight={12}
            labelTextColor={{
                from: 'color',
                modifiers: [
                    ['darker', 1.6]
                ]
            }}
            legends={[
                {
                    dataFrom: 'keys',
                    anchor: 'bottom-right',
                    direction: 'column',
                    justify: false,
                    translateX: 120,
                    translateY: 0,
                    itemsSpacing: 2,
                    itemWidth: 100,
                    itemHeight: 20,
                    itemDirection: 'left-to-right',
                    itemOpacity: 0.85,
                    symbolSize: 20,
                    effects: [
                        {
                            on: 'hover',
                            style: {
                                itemOpacity: 1
                            }
                        }
                    ]
                }
            ]}
            role="application"
            ariaLabel="Nivo bar chart"
            barAriaLabel={e => e.id + ": " + e.formattedValue + " on " + indexBy + ": " + e.indexValue}
        />
    );
};

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

    if (!data) return <Loading />;

    const matchesPerDay = Object.keys(data.matches_per_day).reduce((acc, date) => {
        const day = getDayOfWeek(date);
        if (!acc[day]) {
            acc[day] = 0;
        }
        acc[day] += data.matches_per_day[date];
        return acc;
    }, {} as Record<string, number>);

    const matchesPerDayArray = Object.keys(matchesPerDay).map(day => ({
        day,
        matches: matchesPerDay[day]
    }));

    const averageUserScoreData = Object.keys(data.average_user_score).map(date => ({
        date,
        averageScore: data.average_user_score[date]
    }));

    const aiPerformanceData = Object.keys(data.ai_performance).map(aiType => ({
        id: aiType,
        label: aiType,
        value: data.ai_performance[aiType].matches_played
    }));

    const userWinRatesData = Object.keys(data.user_win_rates).map(user => ({
        x: data.user_win_rates[user].user_name,
        y: data.user_win_rates[user].win_rate
    }));

    const aiWinRatesData = Object.keys(data.ai_win_rates).map(aiType => ({
        x: aiType,
        y: data.ai_win_rates[aiType].win_rate
    }));


    const scoreDistributionData = [
        {
            id: 'user',
            label: 'User',
            value: data.score_distribution.reduce((acc, sd) => acc + sd.user_score, 0)
        },
        {
            id: 'ai',
            label: 'AI',
            value: data.score_distribution.reduce((acc, sd) => acc + sd.ai_score, 0)
        }
    ];

    const playerActivityData = Object.keys(data.player_activity).map(date => ({
        x: date,
        y: data.player_activity[date]
    }));

    return (
        <div className='bg-nyanza'>
            <h2 className='text-xl mt-5 font-bold text-center'>Matches Per Day</h2>
            <div style={{ height: 400 }}>
                <MyResponsiveBar data={matchesPerDayArray} keys={['matches']} indexBy="date" xLegend="Date" yLegend="Matches" />
            </div>

            <h2 className='text-xl mt-5 font-bold text-center'>Average User Score Over Past Month</h2>
            <div style={{ height: 400 }}>
                <MyResponsiveBarAverageScore data={averageUserScoreData} keys={['averageScore']} indexBy="date" xLegend="Date" yLegend="Average Score" />
            </div>

            <h2 className='text-xl mt-5 font-bold text-center'>Matches Played Per AI</h2>
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
                    colors={{ scheme: 'pink_yellowGreen' }}
                />
            </div>

            <h2 className='text-xl mt-5 font-bold text-center'>User Win Rates</h2>
            <div style={{ height: 400 }}>
                <ResponsiveBar
                    data={userWinRatesData}
                    keys={['y']}
                    indexBy="x"
                    margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
                    padding={0.3}
                    axisTop={null}
                    axisRight={null}
                    axisBottom={{
                        legend: 'User Name',
                        legendPosition: 'middle',
                        legendOffset: 32
                    }}
                    axisLeft={{
                        legend: 'Win Rate (%)',
                        legendPosition: 'middle',
                        legendOffset: -40
                    }}
                    colors={{ scheme: 'pink_yellowGreen' }}
                />
            </div>

            <h2 className='text-xl mt-5 font-bold text-center'>AI Win Rates</h2>
            <div style={{ height: 400 }}>
                <ResponsiveBar
                    data={aiWinRatesData}
                    keys={['y']}
                    indexBy="x"
                    margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
                    padding={0.3}
                    axisTop={null}
                    axisRight={null}
                    axisBottom={{
                        legend: 'AI Type',
                        legendPosition: 'middle',
                        legendOffset: 32
                    }}
                    axisLeft={{
                        legend: 'Win Rate (%)',
                        legendPosition: 'middle',
                        legendOffset: -40
                    }}
                    colors={{ scheme: 'pink_yellowGreen' }}
                />
            </div>

            <h2 className='text-xl mt-5 font-bold text-center'>Score Distribution</h2>
            <div style={{ height: 400 }}>
                <ResponsivePie
                    data={scoreDistributionData}
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
                    colors={{ scheme: 'pink_yellowGreen' }}
                />
            </div>

            <h2 className='text-xl mt-5 font-bold text-center'>Player Activity</h2>
            <div style={{ height: 400 }}>
                <ResponsiveLine
                    data={[{ id: 'active_players', data: playerActivityData }]}
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
                        legend: 'Active Players',
                        legendOffset: -40,
                        legendPosition: 'middle'
                    }}
                    colors={{ scheme: 'pink_yellowGreen' }}
                />
            </div>
        </div>
    );
};

export default Statistics;
