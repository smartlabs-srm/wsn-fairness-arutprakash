/****************************************************************************
  This file is part of LoLA.

  LoLA is free software: you can redistribute it and/or modify it under the
  terms of the GNU Affero General Public License as published by the Free
  Software Foundation, either version 3 of the License, or (at your option)
  any later version.

  LoLA is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for
  more details.

  You should have received a copy of the GNU Affero General Public License
  along with LoLA. If not, see <http://www.gnu.org/licenses/>.
****************************************************************************/

/*!
\file
\author Karsten
\status new

\brief Class for firelist generation. Use up sets for bound calcuations
*/

#include <Core/Dimensions.h>
#include <Exploration/Firelist.h>
#include <Exploration/FirelistStubbornComputeBound.h>
#include <Exploration/FirelistStubbornDeadlock.h>
#include <Exploration/StatePredicateProperty.h>
#include <Formula/StatePredicate/StatePredicate.h>
#include <Formula/StatePredicate/AtomicStatePredicate.h>
#include <Net/Net.h>
#include <Net/NetState.h>
#include <Net/Transition.h>

FirelistStubbornComputeBound::FirelistStubbornComputeBound(StatePredicate *p) :
    predicate(p), dfsStack(new arrayindex_t[Net::Card[TR]]), onStack(new bool[Net::Card[TR]]()),
    dl(new FirelistStubbornDeadlock())
{}

FirelistStubbornComputeBound::~FirelistStubbornComputeBound()
{
    delete[] dfsStack;
    delete[] onStack;
    delete dl;
}

arrayindex_t FirelistStubbornComputeBound::getFirelist(NetState &ns, arrayindex_t **result)
{
    if (ns.CardEnabled == 0)
    {
        // found a deadlock - return empty firelist
        * result = new arrayindex_t[1];
        return 0;
    }
    scapegoatNewRound();
    bool needEnabled = false;
    arrayindex_t stackpointer = reinterpret_cast<AtomicStatePredicate*>(predicate)->getDownSet(dfsStack, onStack, &needEnabled);
    arrayindex_t cardEnabled = 0;

    // loop until all stack elements processed
    for (arrayindex_t firstunprocessed = 0; firstunprocessed < stackpointer; ++firstunprocessed)
    {
        arrayindex_t currenttransition = dfsStack[firstunprocessed];
        arrayindex_t *mustbeincluded;
        arrayindex_t  cardmustbeincluded;
        if (ns.Enabled[currenttransition])
        {
            ++cardEnabled;
            mustbeincluded = Transition::Conflicting[currenttransition];
            cardmustbeincluded = Transition::CardConflicting[currenttransition];
        }
        else
        {

	    arrayindex_t scapegoat = Firelist::selectScapegoat(ns,currenttransition);

            mustbeincluded = Net::Arc[PL][PRE][scapegoat];
            cardmustbeincluded = Net::CardArcs[PL][PRE][scapegoat];
        }
        for (arrayindex_t i = 0; i < cardmustbeincluded; ++i)
        {
            const arrayindex_t t = mustbeincluded[i];
            if (!onStack[t])
            {
                dfsStack[stackpointer++] = t;
                onStack[t] = true;
            }
        }
    }
        // if up set for deadlock AP is required but there is an enabled
        // transition so far, this enabled transition serves as a valid
        // up set
        arrayindex_t size = cardEnabled;
        * result = new arrayindex_t [cardEnabled ? cardEnabled : 1];
        for (arrayindex_t i = 0; i < stackpointer; ++i)
        {
            const arrayindex_t t = dfsStack[i];
            if (ns.Enabled[t])
            {
                (*result)[--cardEnabled] = t;
            }
            onStack[t] = false;
        }
        return size;
}

Firelist *FirelistStubbornComputeBound::createNewFireList(SimpleProperty *property)
{
    return new FirelistStubbornComputeBound((reinterpret_cast<StatePredicateProperty *>
            (property))->getPredicate());
}
