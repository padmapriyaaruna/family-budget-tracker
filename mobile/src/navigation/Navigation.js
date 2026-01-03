import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Import screens (to be created)
// import LoginScreen from '../screens/LoginScreen';
// import IncomeScreen from '../screens/IncomeScreen';
// import AllocationsScreen from '../screens/AllocationsScreen';
// import ExpensesScreen from '../screens/ExpensesScreen';
// import ReviewScreen from '../screens/ReviewScreen';
// import ChatbotScreen from '../screens/ChatbotScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Main tabs for authenticated users
const MainTabs = () => {
    return (
        <Tab.Navigator
            screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                    let iconName;

                    if (route.name === 'Income') {
                        iconName = 'attach-money';
                    } else if (route.name === 'Allocations') {
                        iconName = 'account-balance';
                    } else if (route.name === 'Expenses') {
                        iconName = 'shopping-cart';
                    } else if (route.name === 'Review') {
                        iconName = 'assessment';
                    } else if (route.name === 'Chatbot') {
                        iconName = 'chat';
                    }

                    return <Icon name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#4CAF50',
                tabBarInactiveTintColor: 'gray',
                headerShown: false,
            })}>
            {/* <Tab.Screen name="Income" component={IncomeScreen} />
      <Tab.Screen name="Allocations" component={AllocationsScreen} />
      <Tab.Screen name="Expenses" component={ExpensesScreen} />
      <Tab.Screen name="Review" component={ReviewScreen} />
      <Tab.Screen name="Chatbot" component={ChatbotScreen} /> */}
        </Tab.Navigator>
    );
};

// Root navigation
const Navigation = () => {
    // TODO: Check authentication status from AsyncStorage
    const isAuthenticated = false;

    return (
        <NavigationContainer>
            <Stack.Navigator>
                {!isAuthenticated ? (
                    {/* Authentication screens */ }
                    // <Stack.Screen name="Login" component={LoginScreen} options={{headerShown: false}} />
                ) : (
                    {/* Main app */ }
                    < Stack.Screen
            name="Main"
                component={MainTabs}
                options={{ headerShown: false }}
          />
        )}
            </Stack.Navigator>
        </NavigationContainer>
    );
};

export default Navigation;
